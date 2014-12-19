"""
Grab temperature data from arduino via the serial port
and send it to a remote server via sockets
"""

import serial
import datetime
import logging
import socket
import sys, getopt
import json


def error_handler(errmsg, message, stop=True):
    """
    Handle Errors for main function
    errmsg: the exception error message
    message: additional message
    stop: default=True, stops exectution of code
    """
    message += " Error Code: " + str(errmsg[0]) + " - " + str(errmsg[1])
    print message
    rightnow = str(datetime.datetime.now())
    logging.debug(rightnow + ": " + message)
    if stop:
        sys.exit()


def main(argv):
    """" Run Main """

    opts, args = getopt.getopt(argv[1:], "hs:a:p:", ["help", "serial=", "addr=", "port="])
    for opt, arg in opts:
        if opt == '-h':
            print "-s --serial: serail port for arduino, string.  ex: '/dev/ttyUSB0'\n" + \
            "-a --addr: server netwrok address, string. ex: '127.0.0.1'\n" + \
            "-p --port: server port, integer. ex: 80"
            sys.exit()
        elif opt in ('-s', '--serial'):
            serialport = arg
        elif opt in ('-a', '--addr'):
            host = arg
        elif opt in ('-p', '--port'):
            port = arg

    logging.basicConfig(filename='serial2socket.log', level=logging.DEBUG)
    start = datetime.datetime.now()
    tsstart = start
    message = "serial2socket started at " + str(start)
    logging.info(message)

    # set up serial connection
    try:
        ser = serial.Serial(serialport, 9600)
    except OSError, errmsg:
        message = "Serial Port does not exist or is not accessible."
        error_handler(errmsg, message)

    # Set up socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, errmsg:
        message = "Failed to create socket."
        error_handler(errmsg, message)
    print "Socket Created"

    # Create connection:
    try:
        s.connect((host, port))
    except socket.error, errmsg:
        message = "Unable to establish network connection."
        error_handler(errmsg, message)

    i = 0
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
            data = {'datetime':rightnow, 'temperature':temperature}
            s.send(json.dumps(data))
            print json.loads(s.recv(1024))
            i = 0           
            tsstart = datetime.datetime.now()

    s.close()

if __name__ == '__main__':
    main(sys.argv)

