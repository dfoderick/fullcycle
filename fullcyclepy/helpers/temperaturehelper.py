'''read temperature on sensor connected to rpi'''
try:
    import Adafruit_DHT
except BaseException:
    pass

def readtemperature():
    #pin 2 or 4 = power, pin 6 = gnd, pin 7 = gpio4
    #https://www.raspberrypi.org/documentation/usage/gpio-plus-and-raspi2/README.md
    humidity, temperature = Adafruit_DHT.read_retry(22, 4)
    return humidity, temperature
