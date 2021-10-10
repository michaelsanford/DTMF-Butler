# pylint: disable=C0321, C0114, W0702, C0103, C0301, R1710
from os import getenv
from time import sleep
import sys
import serial
import sanity

BAUDRATE = int(getenv('BAUDRATE', '57600'))
DIAL = getenv('DIAL', '6')
TIMEOUT = int(getenv('TIMEOUT', '3'))
DTMF_DURATION = getenv('DTMF_DURATION', '255')

# Sanity checks
if BAUDRATE not in sanity.BAUDRATES:
    print(
        f"FATAL: 'BAUDRATE' of {BAUDRATE} provided is invalid, must be one of {sanity.BAUDRATES}.")
    sys.exit(1)

if DIAL not in sanity.DIALABLES:
    print(
        f"FATAL: Provided 'DIAL' of {DIAL} is invalid, must be one of {sanity.DIALABLES}.")
    sys.exit(1)

if not 1 <= int(DTMF_DURATION) <= 255:
    print(
        f"FATAL: Provided 'DTMF_DURATION' of {DTMF_DURATION} is invalid, must be between 1 and 255.")
    sys.exit(1)

if not 1 <= TIMEOUT <= sanity.TIMOUT_MAX:
    print(
        f"FATAL: Provided 'TIMEOUT' of {TIMEOUT} is invalid, must be between 1 and {sanity.TIMOUT_MAX}.")
    sys.exit(1)


# Open the modem
modem = serial.Serial(port='/dev/ttyACM0', baudrate=BAUDRATE,
                      timeout=TIMEOUT, write_timeout=TIMEOUT)


def configure_modem():
    """Configure the modem or terminate the program"""

    try:
        modem.flushInput()
        modem.flushOutput()

        if not AT():
            print("FATAL: Unable to reach the modem.")
            sys.exit(2)

        if not AT("Z"):
            print("ERROR: Unable to reset the modem.")

        if not AT("V1"):
            print("ERROR: Unable to set V1.")

        if not AT("X0"):
            print("FATAL: Unable to disable dial done detection.")
            sys.exit(3)

        if not AT(f"S11={DTMF_DURATION}"):
            print("ERROR: Unable to set S11 register.")

    except:
        print("FATAL: Unable to initialize the modem.")
        sys.exit(1)


def AT(command=""):
    """Sends an AT command to the modem

    Keyword arguments:
    command -- A Hayes-compatible AT command (default "").
    """

    try:
        modem.flushInput()
        modem.flushOutput()

        modem.write(f"AT{command}\r".encode())

        r = modem.readline() + modem.readline()
        r = r.rstrip()

        if r is not "".encode():
            print(r.decode())
            return "OK" in r.decode()

    except:
        print(Exception)
        print(f"COMMAND FAILED: {command}")
        return False


# def health(ok):
#     with open("HEALTH", "w") as h:
#         h.write(f"OK {time.ctime()}" if ok else "FAILED")


configure_modem()


print("LISTENING...")

while True:
    response = modem.readline().rstrip()

    if response is not "".encode():
        print(response.decode())

    sleep(1)

    # health(AT())

    if "R".encode() in response:
        print("ANSWERING DOOR")
        AT(f"D{DIAL}")
        AT("H")
