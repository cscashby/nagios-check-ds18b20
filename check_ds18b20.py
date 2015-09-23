#!/usr/bin/env python
# coding=utf-8

"""
Author: Christian Ashby
September 2016
@babelmonk
"""

import optparse
import sys
import time
from temp import Temp

NAGIOS_STATUS = { "OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3 }

parser = optparse.OptionParser()
parser.set_usage("%prog [options] <sensorID>")
parser.add_option("-t", "--timeout", dest="timeout", metavar="TIMEOUT", type="int", default="5",
	help="Timeout (s) for sensor to return valid data, default is 5s. NOTE, nagios may impose a timeout shorter than this value")
parser.add_option("-d", "--directory", dest="baseDir", metavar="BASEDIR", type="string", default="/sys/bus/w1/devices",
	help="Directory for one-wire devices folder, defaults to /sys/bus/w1/devices")
parser.add_option("-w", "--lowarning", dest="LoWarnTemp", type="float", default="15",
	help="Warning minimum temperature in deg C, defaults to 25")
parser.add_option("-c", "--locritical", dest="LoCritTemp", type="float", default="12",
	help="Critical minimum temperature in deg C, defaults to 35")
parser.add_option("-W", "--hiwarning", dest="HiWarnTemp", type="float", default="25",
	help="Warning maximum temperature in deg C, defaults to 25")
parser.add_option("-C", "--hicritical", dest="HiCritTemp", type="float", default="35",
	help="Critical maximum temperature in deg C, defaults to 35")
(options, args) = parser.parse_args()

if len(args) != 1:
	parser.print_help(file=sys.stderr)
	sys.exit(1)

sensorid = args[0]

# Kick off the sensor code to read the temperature
cTemp = Temp(sensorid=sensorid, sensordir=options.baseDir)
cTemp.start()

startTime = time.clock()
# Loop waiting for ready status while checking for timeouts / errors
while not cTemp.isReady() and not cTemp.isError():
	if (startTime + options.timeout) < time.clock():
		print "UNKNOWN: sensor {0} - timeout reading temperature".format(sensorid)
		sys.exit(NAGIOS_STATUS['UNKNOWN'])

# We could have got here if there was an error, in which case the library writes to stderr
# but we need to provide nagios with useful status as well
if cTemp.isError():
	print "UNKNOWN: sensor {0} - couldn't be read".format(sensorid)
	sys.exit(NAGIOS_STATUS['UNKNOWN'])

# Good, we have a temperature, we can proceed
t = cTemp.getCurrentTemp()
if t > options.HiCritTemp:
	print "CRITICAL: {0:0.3f}C sensor {1} - over temperature | temp={0:0.3f};{2:0.3f};{3:0.3f}".format(
		t, sensorid, options.HiCritTemp, options.HiWarnTemp)
	sys.exit(NAGIOS_STATUS['CRITICAL'])
elif t < options.LoCritTemp:
	print "CRITICAL: {0:0.3f}C sensor {1} - under temperature | temp={0:0.3f};{2:0.3f};{3:0.3f}".format(
		t, sensorid, options.LoCritTemp, options.LoWarnTemp)
	sys.exit(NAGIOS_STATUS['CRITICAL'])
elif t > options.HiWarnTemp:
	print "WARNING: {0:0.3f}C sensor {1} - over temperature | temp={0:0.3f};{2:0.3f};{3:0.3f}".format(
		t, sensorid, options.HiCritTemp, options.HiWarnTemp)
	sys.exit(NAGIOS_STATUS['WARNING'])
elif t < options.LoWarnTemp:
	print "WARNING: {0:0.3f}C sensor {1} - under temperature | temp={0:0.3f};{2:0.3f};{3:0.3f}".format(
		t, sensorid, options.LoCritTemp, options.LoWarnTemp)
	sys.exit(NAGIOS_STATUS['WARNING'])
else:
	print "OK: {0:0.3f}C sensor {1} | temp={0:0.3f};{2:0.3f};{3:0.3f}".format(
		t, sensorid, options.HiCritTemp, options.HiWarnTemp)
	sys.exit(NAGIOS_STATUS['OK'])
