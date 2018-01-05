#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import dht11
import graphitesend
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

#define the pin that goes to the circuit
pin_for_temp    = 15
pin_for_light   = 40

graphite_server = config.get('DEFAULT','graphite_server')

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.cleanup()

def readLight (pin_for_light):
    count = 0

    #Output on the pin for
    GPIO.setup(pin_for_light, GPIO.OUT)
    GPIO.output(pin_for_light, GPIO.LOW)
    time.sleep(0.1)

    #Change the pin back to input
    GPIO.setup(pin_for_light, GPIO.IN)

    #Count until the pin goes high
    while (GPIO.input(pin_for_light) == GPIO.LOW):
        count += 1
        if count >= 10000000:
          return count

    return count

def readTemperatureAndHumidity(pin_for_temp):
    instance = dht11.DHT11(pin_for_temp)
    result = instance.read()

    if result.is_valid():
        return result
    else:
        print("Error: %d" % result.error_code)
        return False

def sendData(metric, value):
    try:
        g = graphitesend.init(graphite_server=graphite_server)
        print g.send(metric, value)
    except Exception as e:
        print e
        pass

try:
    while True:
        result = readTemperatureAndHumidity(pin_for_temp)
        if (result != False):
            sendData('raspberry.temperature', result.temperature)
            sendData('raspberry.humidity', result.humidity)

        sendData('raspberry.light', readLight(pin_for_light))

        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
