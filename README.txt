Lutfi Berker Evliyaoglu
Internet of Things Final Project
Plant Selector

First of all to run this program you need to have adafruit_blinka, RPi.GPIO,
and BeautifulSoup libraries.

I connected my sensor like:
GPIO 18 -> DHT11 temperature and humidity sensor
GPIO 21 -> Rain drop sensor
pin 21 -> soil moisture sensor
UV light sensor -> mcp3008 adc connections channel0

To run the code you need to run with python3 and you have to wait
 at least 1 minute. After the sensors get data you click the Ctrl+C
 to terminate the program. You will see a list if you can satisfy
 the conditions for a plant to grow. If not you will see a blank list. 
