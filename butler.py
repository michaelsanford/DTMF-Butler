# pylint: disable=C0321, C0114, W0702, C0103, C0301, R1710, W0603, W0621
from os import getenv
from time import sleep
from pathlib import Path
import logging
import sys
import serial
import checks

DIAL = getenv('DIAL', '6')
TIMEOUT = int(getenv('TIMEOUT', '3'))
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN', None)
TELEGRAM_USERS = getenv('TELEGRAM_USERS', None)
NOTIFY_ONLY = bool(getenv('NOTIFY_ONLY', None))

hc_fail_counter = 0
modem_listen = True

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('main')

if DIAL not in checks.DIALABLES:
    log.fatal("'DIAL' of %s is invalid, must be one of %s.",
              DIAL, checks.DIALABLES)
    sys.exit(1)

if not 1 <= TIMEOUT <= checks.TIMOUT_MAX:
    log.fatal("'TIMEOUT' of %s is invalid, must be between 1 and %s",
              TIMEOUT, checks.TIMOUT_MAX)
    sys.exit(1)

if TELEGRAM_TOKEN is not None and TELEGRAM_USERS is not None:
    import telegram

if NOTIFY_ONLY:
    log.info("Notify-only enabled - dialing blocked.")

# Open the modem
modem = serial.Serial(port='/dev/ttyACM0', baudrate=57600,
                      timeout=TIMEOUT, write_timeout=TIMEOUT)


def configure_modem():
    """Configure the modem or terminate the program"""

    log = logging.getLogger('configure')

    try:
        if not AT():
            log.fatal("Unable to reach the modem.")
            sys.exit(1)

        if not AT("Z"):
            log.error("Unable to reset the modem.")

        if not AT("V1"):
            log.error("Unable to set V1.")

        if not AT("X0"):
            log.fatal("Unable to disable dial done detection.")
            sys.exit(3)

        # Wait for Carrier after Dial (seconds)
        if not AT("S7=1"):
            log.error("Unable to set S7 register")

        # Carrier Detect Response Time (0.1 seconds)
        if not AT("S9=10"):
            log.error("Unable to set S9 register")

        # Delay between Loss of Carrier and Hang-Up (0.1 seconds)
        if not AT("S10=10"):
            log.error("Unable to set S10 register")

        # Delay before Force Disconnect (seconds)
        if not AT("S38=1"):
            log.error("Unable to set S38 register")

        if not AT("+FCLASS=8"):
            log.fatal("Unable to set voice mode.")
            sys.exit(1)

    except:
        log.fatal("Unable to initialize the modem, %s:", Exception.__name__)
        log.fatal(Exception.with_traceback())

        if "telegram" in sys.modules:
            telegram.send("❌ The Butler was <u>UNABLE TO START</u>.")

        sys.exit(1)


def AT(command=""):
    """Sends an AT command to the modem

    Keyword arguments:
    command -- A Hayes-compatible AT command (default "").
    """

    log = logging.getLogger('AT')

    global modem_listen
    modem_listen = False

    try:
        modem.write(f"AT{command}\r".encode())

        cmd = modem.readline().rstrip().decode()
        r = modem.readline().rstrip().decode()

        log.info("%s -> %s", cmd, r)

        modem.flush()
        modem_listen = True
        return "OK" in r

    except:
        log.error("Command AT%s failed with %s:", command, Exception.__name__)
        log.error(Exception.with_traceback())
        modem_listen = True
        return False


def health_check():
    """
    Internal detector for Docker's HEALTHCHECK
    """
    global hc_fail_counter
    log = logging.getLogger('healthcheck')
    healthy = modem.isOpen()
    file = Path("/tmp/HEALTH_OK")

    if healthy:
        file.touch(exist_ok=True)
    else:
        hc_fail_counter += 1
        log.error("Health check failed %d times.", hc_fail_counter)
        file.unlink(missing_ok=True)

        if hc_fail_counter > 5:
            log.fatal("Exiting.")
            sys.exit(1)


def answer():
    """
    Answers the modem in voice mode and presses the
    configured DIAL button before hanging up
    """

    log = logging.getLogger('answer')

    if "telegram" in sys.modules:
        telegram.send("🚪🛎 - Answering the door...")

    if not AT("+FCLASS=8"):
        log.error("Failed set voice mode.")

    if not AT("+VLS=1"):
        log.error("Failed answer voice.")

    if not AT(f"+VTS={DIAL}"):
        log.error("Failed dial")
        if "telegram" in sys.modules:
            telegram.send("❌ <u>FAILED</u> to open the door.")
    else:
        log.info("Dial success.")
        if "telegram" in sys.modules:
            telegram.send("✅ The door has <i>OPENED</i>.")

    if not AT("+VLS=0"):
        log.info("Failed to hang up voice, trying hard hook.")
        AT("H")


configure_modem()

log.info("Monitoring modem...")

if "telegram" in sys.modules:
    telegram.send("🧷 The Butler has <u>RESTARTED</u>.")

while True:

    log = logging.getLogger('listener')

    health_check()

    sleep(2)

    if modem_listen:
        response = modem.readline().rstrip().decode()

        if response != "":
            log.info(response)

        if "R" in response:
            if "telegram" in sys.modules:
                telegram.send("🔔 Intercom is ringing...")

            if not NOTIFY_ONLY:
                answer()
