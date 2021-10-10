"""
Sanity checks for environment-based configuration provided by the user.
"""
import sys

BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
             9600, 19200, 38400, 57600, 115200)

DIALABLES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#']

TIMOUT_MAX = sys.maxsize
