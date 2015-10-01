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
parser.set_usage("%prog [options] <sensorID>\n\n\tNOTE: for threshold value format see\nhttps://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT")
parser.add_option("-t", "--timeout", dest="timeout", metavar="TIMEOUT", type="int", default="5",
	help="Timeout (s) for sensor to return valid data, default is 5s. NOTE, nagios may impose a timeout shorter than this value")
parser.add_option("-d", "--directory", dest="baseDir", metavar="BASEDIR", type="string", default="/sys/bus/w1/devices",
	help="Directory for one-wire devices folder, defaults to /sys/bus/w1/devices")
parser.add_option("-w", "--lowarning", dest="WarnTemp", type="string", default="15:25",
	help="Warning temperature (min:max) in deg C, defaults to 15:25")
parser.add_option("-c", "--locritical", dest="CritTemp", type="string", default="12:35",
	help="Critical temperature (min:max) in deg C, defaults to 12:35")
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

# Work out threshold range values
critTemp = options.CritTemp.split(':')
warnTemp = options.WarnTemp.split(':')
if len(critTemp) > 1:
	hiCritTemp = (float(0) if critTemp[1] == "" else float(critTemp[1]) if critTemp[1] != "~" else float('inf'))
	loCritTemp = (float(0) if critTemp[0] == "" else float(critTemp[0]) if critTemp[0] != "~" else 0-float('inf'))
else:
	hiCritTemp = float(critTemp[0]) if critTemp[0] != "~" else float('inf')
	loCritTemp = float(0)
	
if len(warnTemp) > 1:
	hiWarnTemp = (float(0) if warnTemp[1] == "" else float(warnTemp[1]) if warnTemp[1] != "~" else float('inf'))
	loWarnTemp = (float(0) if warnTemp[0] == "" else float(warnTemp[0]) if warnTemp[0] != "~" else 0-float('inf'))
else:
	hiWarnTemp = float(warnTemp[0]) if warnTemp[0] != "~" else float('inf')
	loWarnTemp = float(0)

# We could have got here if there was an error, in which case the library writes to stderr
# but we need to provide nagios with useful status as well
if cTemp.isError():
	print "UNKNOWN: sensor {0} - couldn't be read".format(sensorid)
	sys.exit(NAGIOS_STATUS['UNKNOWN'])

# Good, we have a temperature, we can proceed
t = cTemp.getCurrentTemp()
if t > hiCritTemp:
	print "CRITICAL: {0:0.1f}C sensor {1} - over temperature {4:0.3f}:{5:0.3f} | temp={0:0.3f};{2};{3}".format(
		t, sensorid, options.WarnTemp, options.CritTemp, loCritTemp, hiCritTemp)
	sys.exit(NAGIOS_STATUS['CRITICAL'])
elif t < loCritTemp:
	print "CRITICAL: {0:0.1f}C sensor {1} - under temperature {4:0.3f}:{5:0.3f} | temp={0:0.3f};{2};{3}".format(
		t, sensorid, options.WarnTemp, options.CritTemp, loCritTemp, hiCritTemp)
	sys.exit(NAGIOS_STATUS['CRITICAL'])
elif t > hiWarnTemp:
	print "WARNING: {0:0.1f}C sensor {1} - over temperature {4:0.3f}:{5:0.3f} | temp={0:0.3f};{2};{3}".format(
		t, sensorid, options.WarnTemp, options.CritTemp, loWarnTemp, hiWarnTemp)
	sys.exit(NAGIOS_STATUS['WARNING'])
elif t < loWarnTemp:
	print "WARNING: {0:0.1f}C sensor {1} - under temperature {4:0.3f}:{5:0.3f} | temp={0:0.3f};{2};{3}".format(
		t, sensorid, options.WarnTemp, options.CritTemp, loWarnTemp, hiWarnTemp)
	sys.exit(NAGIOS_STATUS['WARNING'])
else:
	print "OK: {0:0.1f}C sensor {1} | temp={0:0.3f};{2};{3}".format(
		t, sensorid, options.WarnTemp, options.CritTemp)
	sys.exit(NAGIOS_STATUS['OK'])
