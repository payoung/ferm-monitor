"""
Grab temperature data from arduino via the serial port
and sends it to a remote server via sockets
"""

import serial
import datetime
import logging


def main():
    """" Run Main """
    logging.basicConfig(filename='serial2socket.log', level=logging.INFO)
    
    start = datetime.datetime.now()
    tsstart = start
    message = "serial2socket started at " + str(start)
    logging.info(message)
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    i = 0
    j = 0
    tempvals = []
    
    # clear out the first few readlines of ser as it can contain weird values
    for _ in range(2):
        ser.readline()

    # collect the serial data, average it
    while True:
        line = ser.readline()

        try:
            tempvals.append(float(line))
        except ValueError:
            rightnow = datetime.datetime.now()
            message = str(rightnow) + ": Float Conversion Exception: " \
            + line + "\n Time Since Start: " + str(rightnow-start)
            logging.info(message)

        i += 1

        if i >= 10:
            rightnow = datetime.datetime.now()
            timestamp = rightnow + (rightnow - tsstart)/2
            temperature = sum(tempvals)/float(len(tempvals))
            print temperature, timestamp
            i = 0           
            tsstart = datetime.datetime.now()


if __name__ == '__main__':
    main()

