# SPDX-FileCopyrightText: Copyright (c) 2020 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_sht4x
from flask import Flask, Response
from prometheus_client import Counter, Gauge, start_http_server, generate_latest
import datetime
import pytemperature
import logging

FORMAT = '%(message)s'
CURRENT_TIMESTAMP=datetime.date.today()

content_type = str('text/plain; version=0.0.4; charset=utf-8')

def get_temperature_readings():
	i2c = board.I2C()  # uses board.SCL and board.SDA
	sht = adafruit_sht4x.SHT4x(i2c)
#	print("Found SHT4x with serial number", hex(sht.serial_number))
	sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
#	print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])
	temperature, relative_humidity = sht.measurements
	tempfahrenheit = pytemperature.c2f(temperature) 
	logging.debug("Temperature-F: {0:.2f} ,Temperature-C: {1:.2f} ,Relative Humidity: {2:.2f} %RH ".format(tempfahrenheit,temperature,relative_humidity))
#	print("Temperature: %0.1f C" % temperature)
#	print("Humidity: %0.1f %%" % relative_humidity)
#	print("")
	response = {"temperature": temperature, "tempfahrenheit": tempfahrenheit, "humidity": relative_humidity}
	return response

app = Flask(__name__)

current_humidity = Gauge(
	'current_humidity',
	'the current humidity percentage, this is a gauge as the value can increase or decrease',
	['room']
)

current_temperature = Gauge(
	'current_temperature',
	'the current temperature in celsius, this is a gauge as the value can increase or decrease',
	['room']
)

current_tempfahrenheit = Gauge(
	'current_tempfahrenheit',
	'the current temperature in fahrenheit, this is a gauge as the value can increase or decrease',
	['room']
)

@app.route('/metrics')
def metrics():
	metrics = get_temperature_readings()
	current_humidity.labels('basement').set(metrics['humidity'])
	current_temperature.labels('asement').set(metrics['temperature'])
	current_tempfahrenheit.labels('asement').set(metrics['tempfahrenheit'])
	return Response(generate_latest(), mimetype=content_type)

if __name__ == '__main__':
	logging.basicConfig(format=FORMAT,filename='/home/traleigh/logs/'+str(CURRENT_TIMESTAMP)+'-sht45-exporter.log', 
						encoding='utf-8', level=logging.DEBUG) 
	app.run(host='0.0.0.0', port=5000)
