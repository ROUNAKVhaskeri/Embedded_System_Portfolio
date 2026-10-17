import time, dht11,board
import adafruit_dht
class DHT11Sensor:
    def __init__(self,pin=board.D4):
        self.pin = pin
        self.sensor = adafruit_dht.DHT11(pin)
    
    def read(self):
        """Read Temperature and Humidity from DHT11 Sensor.."""
        try:
            humidity = self.sensor.humidity
            temperature = self.sensor.temperature
        except Exception as e:
            humidity = None
            temperature = None
        if humidity is not None and temperature is not None:
            return {
                "temperature":round(temperature,1),
                "humidity":round(humidity,1)
            }

        else:
            return {
                "temperature":None,
                "humidity":None,
                "error":"Failed to read from DHT Sensor"
            }

