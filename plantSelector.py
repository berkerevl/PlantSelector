import RPi.GPIO as GPIO
import dht11
import time
import datetime
import os
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import html
from bs4 import BeautifulSoup
import requests
import string

#soil type
soilType = "clay" 

#create the spi bus
spi = busio.SPI(clock = board.SCK, MISO = board.MISO, MOSI = board.MOSI)

#create the cs 
cs = digitalio.DigitalInOut(board.D22)

#create the mcp object
mcp = MCP.MCP3008(spi, cs)

#create an analog input channel on pin0
chan0 = AnalogIn(mcp, MCP.P0)


#GPIO connections

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN)
GPIO.setup(21, GPIO.IN)
channel = 21
GPIO.setup(channel, GPIO.IN)

#for dht11 sensor
instance = dht11.DHT11(pin=14)

#to open and evaluate the text database
def selection(humid, Temp, light, SMoist, rain):
	f = open('plantsdb.txt','r')
	lines = f.readlines()
	holder = []
	for i in lines:
		newline = i.split(" ")
		if(newline[1] == "clay"):
			if(float(newline[2]) >= humid - 10 and float(newline[2]) <= humid + 10):
				if(Temp >= float(newline[3])and Temp <= float(newline[4])):
					if(float(newline[5]) >= light- 0.2 and float(newline[5]) <= light + 0.2):
						if(float(newline[6]) >= SMoist - 0.2 and float(newline[6]) <= SMoist + 0.2):
							if(float(newline[7]) >= rain - 0.1 and float(newline[7]) <= rain + 0.1):
								holder.append(newline[0])
	return holder
	f.close()

#web scrapping when rain sensor sense rain and rain stops
def scrapfromweb():
	mete_url = "http://www.cnyweather.com/wxraindetail.php?r=wxraindetail.php"
	page_id = "levelb_1"

	response  = requests.get(mete_url)
	soup = BeautifulSoup(response.text, "html.parser")

	Raintable = soup.find('td',attrs ={'class', page_id})
	x = str(Raintable)
	y = (x[21]+x[22]+x[23]+x[24])
	z = float(y)
	return z

#for UV light sensor
def evaluateSensorValue(counterLight, totalLightCounter):

	totalLightCounter = totalLightCounter + 1
	if(chan0.value == 0):
		print ("light is on")
		#print (str(datetime.datetime.now()))
		counterLight = counterLight + 1
		#print (counterLight)
	else:
		print ("light is off")
	return counterLight, totalLightCounter

	#time.sleep(7200) actually this project is a long term program.
    #So the line on the above for every 24 hours calculations.
	time.sleep(4) # I used this line for demo to show you quickly.


#for soil moisture sensor
def callback(channel):
	if(GPIO.input(channel)):
		print ("soil is dry")
		global dryCounter
		dryCounter = dryCounter + 1
	else:
		print ("soil is moisty")
	global totalMoist
	totalMoist = totalMoist + 1

#soil moisture sensor detect the moist
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime = 300)
#calls the event
GPIO.add_event_callback(channel, callback)

#variables and counters for calculation and evaluation

TempSum = 0.0
TempCounter = 0
counterLight = 0
totalLightCounter = 0
HumSum = 0.0
HumCounter = 0
dryCounter = 0
totalMoist = 0
rainCounter = 0
getScrap = False


#main code
try:
	while(True):

		counterLight,totalLightCounter = evaluateSensorValue(counterLight,totalLightCounter)
		result = instance.read()
		rain_drop_state = GPIO.input(18)

		while(True):
			if(rain_drop_state == 0):
				print ("It's Rainy Outside\n")
				time.sleep(6)
				break
			else:
				print ("Not rainy\n")
				RainAvg = scrapfromweb()
				if(RainAvg != 0.0):
					print (RainAvg)
				time.sleep(6)
				break

		if result.is_valid():
			print ("Last valid input: " + str(datetime.datetime.now()))
			print ("temp: %-3.1f C" %result.temperature)
			TempSum = TempSum + result.temperature
			TempCounter = TempCounter + 1
			print ("humidity: %-3.1f %%" % result.humidity)
			HumSum = HumSum + result.humidity
			HumCounter = HumCounter + 1

			time.sleep(6)

except KeyboardInterrupt:

	TempAvg = TempSum / TempCounter
	HumAvg = HumSum / HumCounter
	
	if(dryCounter == 0):
		MoistAvg = 1
	else:
		MoistAvg = 1 - dryCounter / totalMoist

	if(counterLight == 0):
		lightAvg = 0
	else:
		lightAvg = counterLight/ totalLightCounter
	
	plantlist = selection(HumAvg,TempAvg,lightAvg,MoistAvg,RainAvg)
	
	print ("\n")
	#print the list of the plants you can grow
	print (plantlist)
	print ("\nAvg Temp: %-3.1f\n" %TempAvg)
	print ("Humidity Avg: %-3.1f\n" %HumAvg)
	print ("Light frequency %-3.1f \n" %lightAvg)
	print ("moisty %-3.1f \n" %MoistAvg)
	GPIO.cleanup()
