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
from collections import defaultdict


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


def send_data(host, port, data, conn_attempts):
    """ 
    Establish connection to server and send data.  If connection fails:
    If more than 10 consecutive attempts to connect to server
    have failed, than exit program
    Otherwise increment and return the failed connection counter
    """

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host, port))
        soc.send(json.dumps(data))
        print soc.recv(1024)
        conn_attempts = 0
    except socket.error, errmsg:
        if conn_attempts > 10:
            message = "Connection failed after 10 tries, exiting program"
            error_handler(errmsg, message)
        else:
            message = "Connection failed, will attempt again"
            error_handler(errmsg, message, stop=False)
            conn_attempts += 1

    soc.close()
    return conn_attempts


def get_args(argv):
    """ Process and return sys args """
    opts, args = getopt.getopt(argv[1:], "hs:a:p:i:", ["help", "serial=", "addr=", "port=", "id="])
    for opt, arg in opts:
        if opt == '-h':
            print "-s --serial: serail port for arduino, string.  ex: '/dev/ttyUSB0'\n" + \
            "-a --addr: server netwrok address, string. ex: '127.0.0.1'\n" + \
            "-p --port: server port, integer. ex: 80\n" + \
            "-i --id: sensor unit id, string. ex: 'kitchen-sensor-1'"
            sys.exit()
        elif opt in ('-s', '--serial'):
            serialport = arg
        elif opt in ('-a', '--addr'):
            host = arg
        elif opt in ('-p', '--port'):
            port = int(arg)
        elif opt in ('-i', '--id'):
            unit_id = arg


    return serialport, host, port, unit_id



def main(argv):
    """" Run Main """
    serialport, host, port, unit_id = get_args(argv)
    logging.basicConfig(filename='serial2socket.log', level=logging.DEBUG)
    start = datetime.datetime.now()
    tsstart = start
    message = "serial2socket started at " + str(start)
    logging.info(message)
    # Use this to keep track of failed connection attempts, stop after 10
    conn_attempts = 0

    # set up serial connection
    try:
        ser = serial.Serial(serialport, 9600)
        print "Serial connection established"
    except OSError, errmsg:
        message = "Serial Port does not exist or is not accessible."
        error_handler(errmsg, message)
    
    # clear out the first few readlines of ser as it can contain weird values
    for _ in range(10):
        ser.readline()

    # collect the serial data, average it
    i = 0
    tempdata = defaultdict(list)
    while True:
        line = ser.readline()
        serdata = line.split()
        if line.strip() != 'CRC is not valid!':
            tempdata[serdata[0]].append(float(serdata[1]))
        else:
            print line

        i += 1

        # after collecting some data, get the average and send across to server
        if i >= 60:
            rightnow = datetime.datetime.now()
            timestamp = rightnow + (rightnow - tsstart)/2
            avgtempdata = {}
            for key, vals in tempdata.iteritems():
                avgtempdata[key] = sum(vals)/float(len(vals))
                tempdata[key] = []
            print timestamp, avgtempdata 
            data = {'unit_id':unit_id, 'datetime':str(timestamp),
                    'temp data':avgtempdata}
            conn_attempts = send_data(host, port, data, conn_attempts)
            i = 0
            tsstart = datetime.datetime.now()


if __name__ == '__main__':
    main(sys.argv)

