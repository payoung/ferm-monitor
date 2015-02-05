ferm-monitor
============

This repo is the sensor level counterpart to the <a href='https://github.com/payoung/beer-app'>beer-app</a> project.
This code is used to send temperature sensor data to the beer-app sensor server.  

The Setup
---------
The sensor unit consists of two DS18B20 digitial temperature sesnors connected to an Arduino, which is connected via USB to a Raspberry Pi with ethernet/wifi access.  The Arduino reads data from the sensors, converts it to a Celcius temperature and then prints the sensors address (for identification purposes) and the temperature reading to the serial port.  The Raspberry Pi has a python program running that reads the data from the serial port, averages the readings for the sensors, and then sends the temperature averages in JSON format to the beer-app server via a socket connection.

Installation and Operation
--------------------------
Clone the github repo.  Load the arduino sketch `/tempsensor/tempsensor.ino` onto the Arduino.  You will need the <a href='http://playground.arduino.cc/Learning/OneWire'>OneWire library</a> installed in you library directory.  The temperature sensors should be hooked to digital pin 2.  <a href='http://www.hobbytronics.co.uk/ds18b20-arduino'>Here is a guide</a> to setting up the sensor, you will need a 4.7K pull-up resistor.  Addtional sensors can be set up in paralell.

Once you have the Arduino setup, you should be able to see the sensor address and temperature data being printed in the serial monitor.  It will look something like `28FFC81D60144E2 17.75`, where the first value is the sensor address (used for identification when more than one sensor is hooked up) and the second value is temperature in Celcius.

Hook the Arduino up to the Raspberry Pi using a USB cable.  You can use `ls /dev/tty*` to figure out which port the Arduino is communicating through.  This information will be needed to configure the Python program.  You will also need to know the IP address and port of the beer-app sensor server.  If that is unavaliable, this repo contains a socket server that can be used to test that your sensor unit is working correctly.  Simply run the `socket_server.py` program locally (the Raspberry Pi) or on another computer.  If running the server locally, simply use `'0.0.0.0'` as the IP address.  To run the program from the project directory do the following: `python serial2socket.py -s '/dev/ttyUSB0' -a '127.0.0.1' -p 1313 -i 'My-Sensor'`.  The options are as follows:

 - -s --serial: The serial port used for communicating with your arduino, typically `'/dev/ttyUSBXX'` or `'/dev/ttyACMXX'`.  Needs to be a string format.
 - -a --addr: The IP address of the server.  If you are using the socket_server.py program for testing, then use that address.  Otherwise it will be the address of the <a href='https://github.com/payoung/beer-app/blob/master/sensor_server.py'>beer-app sensor server</a>.  String format.
 - -p --port: The port for the sensor server.  The beer-app default port is set to 1313. Integer format.
 - -i --id:  Sensor unit id.  This can be whatever you want it to be, it is used to identify the sensor unit, and distingush it from other units that you may have running.  String format.

If everything is working, you will see the temperature data in JSON format getting printed to console followed by a `{'return':'ok'}` indiciating the the data was successfully recieved by the server.

Additional Info
---------------
The Arduino reads temperature data from the sensors at a rate of approximately once per second.  If multiple sensors are hooked up to the same pin, it randomly polls the sensors for a connection.  Once the temperature data is aquired, it sends the data to the serial port and repeats the process.  The `serial2socket.py` program reads the serial data and 60 times and then averages the data for each sensor and sends it across the network.  This results in data points of approximately one per minute per sensor.  Because the Arduino randomly polls the temperature sensors, there is no garuntee that you will get an equal amount of temperature data from each sensor.  However in my experience with you will get enough data from each sensor in the minute period for a relatively robust average. 

Identifiying the sensors based on their address is a bit tricky.  I typically hold one of the sensors in my hand to warm it up and then monitor the data in the console, and then write down the address and label the sensor.  In the future, it might make sense to allow for sensors to be read from seperate pins, as that would make it much easier to distinguish which sensor is which (this is important to know, in case you have one sensor hooked up to a beer fermentation and the other monitoring ambient temperatures, or another fermenation).

Demo
----

This is a link to a working version of the <a href='https://github.com/payoung/beer-app'>beer-app</a> recieving data from sensor units using the code form this repo: http://beer.pyoung.net/

Other Resources
---------------

Here are a few links to blog posts about the project:

http://www.blog.pyoung.net/2015/01/14/fermentation-temperature-monitor/
http://www.blog.pyoung.net/2015/01/16/beer-app/
http://www.blog.pyoung.net/2015/01/21/adding-additional-temperature-sensors-to-an-arduino/
http://www.blog.pyoung.net/2015/01/28/ds18b20-crc-check-codes/

