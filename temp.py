#!/usr/bin/env python
# coding=utf-8

"""
Author: Christian Ashby
September 2016
@babelmonk
Thanks to: http://raspbrew.tumblr.com/post/44456213110/reading-temperatures-on-a-raspberry-pi-using
"""

from threading import Thread
import time
import sys

class Temp(Thread):
	"""
	 A class for getting the current temp of a DS18B20
	"""
	def __init__(self, sensorid = None, sensordir='/sys/bus/w1/devices', group=None, target=None, name=None, verbose=None):
		super(Temp, self).__init__(group=group, target=target, name=name, verbose=verbose)
		self.sensorid = sensorid
		self.sensordir = sensordir
		self.currentTemp = -999
		self.correctionFactor = 0
		self.enabled = True
		self.error = False
		self.ready = False
		self.daemon = True

	def run(self):
		while True:
			if self.isEnabled():
				filename = self.sensordir + "/" + self.sensorid + "/w1_slave"
				try:
					f = open(filename, 'r')
				except IOError as e:
					sys.stderr.write("Error: File " + filename + " does not exist.\n")
					self.error = True
					return
				
				lines=f.readlines()
				crcLine=lines[0]
				tempLine=lines[1]
				result_list = tempLine.split("=")

				temp = float(result_list[-1])/1000 # temp in Celcius

				temp = temp + self.correctionFactor # correction factor

				#if you want to convert to fahrenheit, uncomment this line
				#temp = (9.0/5.0)*temp + 32  
				
				if crcLine.find("NO") > -1:
					temp = -999
				else:
					self.ready = True

				self.currentTemp = temp
				#print "Current: " + str(self.currentTemp) + " " + str(self.sensorid)

				time.sleep(1)

	#returns the current temp for the probe
	def getCurrentTemp(self):
		return self.currentTemp

	#setter to enable this probe
	def setEnabled(self, enabled):
		self.enabled = enabled
	#getter	   
	def isEnabled(self):
		return self.enabled

	#getter for ready check
	def isReady(self):
		return self.ready

	#getter for error check
	def isError(self):
		return self.error