import smbus2 as smbus
import time
import logging

logger = logging.getLogger(__name__)

class BH1750:
    def __init__(self, bus=1, addr=0x23):
        self.bus = None
        self.addr = addr
        self.bus_num = bus
        self._init_bus()
    
    def _init_bus(self):
        """Initialize I2C bus with error handling"""
        try:
            self.bus = smbus.SMBus(self.bus_num)
            logger.info(f"BH1750 initialized on I2C bus {self.bus_num}")
        except Exception as e:
            logger.error(f"Failed to initialize I2C bus {self.bus_num}: {str(e)}")
            self.bus = None
    
    def read_light(self):
        """Read Lux Value from the sensor"""
        try:
            if self.bus is None:
                self._init_bus()
            
            if self.bus is None:
                return {
                    "lux": None,
                    "error": "I2C bus not available"
                }
            
            # Power on the sensor (0x01)
            try:
                self.bus.write_i2c_block_data(self.addr, 0x00, [0x01])
            except:
                # Fallback to write_byte if write_i2c_block_data fails
                self.bus.write_byte(self.addr, 0x01)
            
            time.sleep(0.01)
            
            # One-time measurement mode with high resolution (0x20)
            try:
                self.bus.write_i2c_block_data(self.addr, 0x00, [0x20])
            except:
                # Fallback to write_byte
                self.bus.write_byte(self.addr, 0x20)
            
            time.sleep(0.25)  # Wait for measurement
            
            # Read 2 bytes from register 0x00
            try:
                data = self.bus.read_i2c_block_data(self.addr, 0x00, 2)
            except:
                # Alternative read approach
                data = self.bus.read_word_data(self.addr, 0x00)
                data = [data & 0xFF, (data >> 8) & 0xFF]
            
            if not data or len(data) < 2:
                raise ValueError(f"Invalid data received: {data}")
            
            # Convert to lux: (MSB << 8) | LSB, then divide by 1.2
            lux = ((data[0] << 8) | data[1]) / 1.2
            logger.info(f"BH1750 read successful - raw: {data}, lux: {round(lux, 1)}")
            return {"lux": round(lux, 1)}
            
        except Exception as e:
            error_msg = f"Error reading BH1750: {str(e)}"
            logger.error(error_msg)
            return {
                "lux": None,
                "error": error_msg
            }