import time, threading
from functools import wraps
import datetime as dt
import RPi.GPIO as GPIO

from sensors.motion_sensor import MotionSensor
from sensors.light_sensor import BH1750
from sensors.temp_humid import DHT11Sensor

from actuators.rgb_led import RGBled

from config import (
    GPIO_MOTION,GPIO_DHT,GPIO_RGB_B,GPIO_RGB_G,GPIO_RGB_R,MAX_BUFFER,logger as log
)

from Mcp.tools_registry import MCP as mcp
class HardwareAPI:
    def __init__(self):
        # ------ Sensors ------
        self.motion_sensor = MotionSensor(GPIO_MOTION)
        self.dht_sensor = DHT11Sensor(GPIO_DHT)
        self.light_sensor = BH1750()

        # ------ Actuators ------
        self.rgb_led = RGBled(GPIO_RGB_R,GPIO_RGB_G,GPIO_RGB_B)
        self.led_mode = "idle"      # Idle | Manual | pattern | Sensor
        self.led_source = None      # DHT  | motion | manual | pattern | light
        self.pattern_thread:threading.Thread | None = None
        self.pattern_stop = threading.Event()

        # ------- Sensor LED States ------
        self.sensor_led_state = {
            "dht" : {"r":0,"g":0,"b":0,"active":False},
            "motion" : {"r":0,"g":0,"b":0,"active":False},
            "light" : {"r":0,"g":0,"b":0,"active":False}
        }

        self._led_lock = threading.Lock()
        self._sensor_lock = threading.Lock()

        
        # ------ Buffers ------
        self.buffers = {
            "dht":[],
            "light":[],
            "motion":[]
        }
        self.threads = {}
        self.stop_flags = {}
        self.temp_threshold = 30
        
        # ------ Startup Test ------

        self.__startup_self_test()

    # ----------------------------------------------------------------------
    # STARTUP SELF TEST
    # ----------------------------------------------------------------------

    def __startup_self_test(self):
        """
        LED-Based Hardware self-test sequence:
        1. WHITE ON (0.5s) -> OFF
        2. Red (Light Sensor alive)
        3. Green (Motion Sensor alive)
        4. Blue (DHT Sensor alive)
        """

        # All LEDs ON
        self.rgb_led.set_color(255,0,0)
        time.sleep(0.3)
        self.rgb_led.set_color(0,255,0)
        time.sleep(0.3)
        self.rgb_led.set_color(0,0,255)
        time.sleep(0.3)
        self.rgb_led.set_color(0,0,0)
        time.sleep(0.2)

    # ----------------------------------------------------------------------
    # LED Logic
    # ----------------------------------------------------------------------


    def _update_led_from_sensors(self):
        """Blend LED colors from active sensors"""
        with self._sensor_lock:
            active_sensors = [
                name for name, state in self.sensor_led_state.items() if state["active"]
            ]
        if not active_sensors:
            self.rgb_led.set_color(0,0,0)
            return
        
        priority = ["motion","dht","light"]     # Needed if single RGB LED is used

        active_by_priority = [s for s in priority if s in active_sensors]

        if active_by_priority:
            selected = active_by_priority[0]
            with self._sensor_lock:
                state = self.sensor_led_state[selected]
                self.rgb_led.set_color(state['r'],state['g'],state['b'])

    def _stop_pattern(self):
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.pattern_stop.set()
            self.pattern_thread.join(timeout=1)
        self.pattern_stop.clear()
        self.pattern_thread = None

    def set_led_manual(self,r,g,b):
        self._stop_pattern()
        self.led_mode = "manual"
        self.led_source = "manual"
        self.rgb_led.set_color(r,g,b)
        return {"status":"led_set","rgb":[r,g,b]}

    def set_led_brightness(self,color:str="rgb",brightness=0):
        self._stop_pattern()
        self.led_mode = "manual"
        self.led_source = "manual"
        val = int((brightness/100)*255)
        if color == "red":
            self.rgb_led.set_color(val,0,0)
        elif color == "green":
            self.rgb_led.set_color(0,val,0)
        elif color == "blue":
            self.rgb_led.set_color(0,0,val)
        elif color == "rgb":
            self.rgb_led.set_color(val,val,val)
        return {
            "status":"led_brightness set",
            "color":color,
            "brightness":brightness
        }

    def set_led_preset(self,preset):
        PRESETS = {
            "red":(255,0,0),
            "green":(0,255,0),
            "blue":(0,0,255),
            "white":(255,255,255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 105, 180),
            "lime": (50, 205, 50),
            "teal": (0, 128, 128),
            "violet": (148, 0, 211),
            "indigo": (75, 0, 130),
            "brown": (165, 42, 42),
            "off":(0,0,0)
        }
        if preset not in PRESETS:
            return {"error":"Unknown Preset","available_colors":list(PRESETS.keys())}
        
        self._stop_pattern()
        self.led_mode = "manual"
        self.led_source = "manual"
        self.rgb_led.set_color(*PRESETS[preset])
        return {
            "Status":"Preset Applied",
            "Color":preset
        }

    def blink_led(self,color:str,count:int=3,interval:float=0.3):
        """Blink LED N times with given color. Blinks 'count' times, each on/off cycle is 'interval' seconds"""
        self._stop_pattern()
        self.led_mode = "manual"
        self.led_source = "manual"
        color_map = {
            "red":(255,0,0),
            "green":(0,255,0),
            "blue":(0,0,255),
            "white":(255,255,255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 105, 180),
            "lime": (50, 205, 50),
            "teal": (0, 128, 128),
            "violet": (148, 0, 211),
            "indigo": (75, 0, 130),
            "brown": (165, 42, 42),
            "off":(0,0,0)
        }
        if color not in color_map:
            return {
                "error":"Unknown Color",
                "available_colors":list(color_map.keys())
            }
        def loop():
            # Blink exactly 'count' times
            for i in range(count):
                if self.pattern_stop.is_set():
                    break
                # LED ON
                self.rgb_led.set_color(*color_map[color])
                time.sleep(interval)
                # LED OFF
                self.rgb_led.set_color(0,0,0)
                time.sleep(interval)
            
            self.rgb_led.set_color(0,0,0)
            self.led_mode = "idle"
        
        self.pattern_thread = threading.Thread(target=loop,daemon=True)
        self.pattern_thread.start()
        return {"status":"Blinking LED Started","color":color,"count":count,"interval":interval}

    def RGB_Pattern(self,duration,color_interval):
        self._stop_pattern()
        self.led_mode = "pattern"
        self.led_source = "pattern"

        colors = [
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (255,255,0),
            (0,255,255),
            (255,0,255),
        ]

        def loop():
            start = time.time()
            idx = 0
            while not self.pattern_stop.is_set():
                if time.time() - start > duration:
                    break

                self.rgb_led.set_color(*colors[idx % len(colors)])
                idx += 1
                time.sleep(color_interval)
            self.rgb_led.set_color(0,0,0)
            self.led_mode = "idle"
        
        self.pattern_thread = threading.Thread(target=loop,daemon=True)
        self.pattern_thread.start()
        return {"status":"Pattern Thread Started."}

    
    def stop_rgb_pattern(self):
        self._stop_pattern()
        self.rgb_led.set_color(0,0,0)
        self.led_mode = "idle"
        self.led_source = "idle"
        return {
            "status":"LED PATTERN IS IDLE...s"
        }
    # ----------------------------------------------------------------------
    # SENSOR MONITORING
    # ----------------------------------------------------------------------

    def _start_monitoring(self,name,fn,led_logic=None):
        
        if name in self.threads:
            return {"error":"Already Running..."}
        
        stop = threading.Event()
        self.stop_flags[name] = stop

        def loop():
            while not stop.is_set():
                data = fn()
                data["timestamp"] = time.time()
                buf = self.buffers[name]
                buf.append(data)
                if len(buf) > MAX_BUFFER:
                    del buf[0]

                if led_logic and self.led_mode == "sensor":
                    r,g,b = led_logic(data)
                    with self._sensor_lock:
                        self.sensor_led_state[name]['r'] = r
                        self.sensor_led_state[name]['g'] = g
                        self.sensor_led_state[name]['b'] = b
                    self._update_led_from_sensors()
                time.sleep(1)
        t = threading.Thread(target=loop,daemon=True)
        self.threads[name] = t

        with self._sensor_lock:
            self.sensor_led_state[name]["active"] = True

        t.start()
        return {"status":f"{name} Started...."}
    
    def _stop_monitoring(self,name):
        if name not in self.threads:
            return {"ststus":f"{name} not Running"}
        
        self.stop_flags[name].set()
        self.threads[name].join(timeout = 1)
        del self.threads[name]

        with self._sensor_lock:
            self.sensor_led_state[name]["active"] = False


        if self.led_mode == "sensor":
            self._update_led_from_sensors()
        else:
            self.rgb_led.set_color(0,0,0)
        return {"success":f"{name} Stopped..."}
    

    def system_status(self):
        """Report Active Sensor and Threshold"""

        return {
            "dht":"dht" in self.threads,
            "light":"light" in self.threads,
            "motion":"motion" in self.threads,
            "temp_threshold":self.temp_threshold,
            "buffer_sizes":{
                k:len(v) for k,v in self.buffers.items()
            },
            "led_mode":self.led_mode,
            "led_source":self.led_source
        }
    
    # ----------------------------------------------------------------------
    # Sensor Functions
    # ----------------------------------------------------------------------

    def start_dht(self,temp_threshold=None):
        def led_logic(d):
            temp = d.get("temperature",0)
            if temp is None:
                self.rgb_led.set_color(0,0,0)
                return
            if temp_threshold is not None:
                self.temp_threshold = temp_threshold
                
            if temp > self.temp_threshold:
                return (255,0,0)
            else:
                return (0,0,0)
        
        self.led_mode = "sensor"
        self.led_source = "dht"
        return self._start_monitoring(
            "dht",
            self.dht_sensor.read,
            led_logic
        )
    
    def start_light(self):
        MAX_LUX = 500
        def led_logic(d):
            lux = d.get("lux",0)

            if lux is None:
                return (0,0,0)
            
            lux = max(0,min(lux,MAX_LUX))
            brightness= int((1-lux/500)*255)

            return (0,brightness,0)
        
        self.led_mode = "sensor"
        self.led_source = "light"
        return self._start_monitoring(
            "light",
            self.light_sensor.read_light,
            led_logic
        )

    def start_motion(self):
        def led_logic(d):
            motion = d.get("motion_detected")
            if motion is None:
                return (0,0,0)
        
            if motion:
                return (0,0,255)
            else:
                return (0,0,0)

        self.led_mode = "sensor"
        self.led_source = "motion"
        return self._start_monitoring(
            "motion",
            self.motion_sensor.read,
            led_logic
        )


    def stop(self,name):
        return self._stop_monitoring(name)

    def set_threshold(self,value):
        self.temp_threshold = value
        return {"threshold":value}

# ----------------------------------------------------------------------
# SINGLETON
# ----------------------------------------------------------------------

hardware = HardwareAPI()

# ----------------------------------------------------------------------
# MCP_Decorator
# ----------------------------------------------------------------------

def hardware_api(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            return {"error":str(e),"fn":func.__name__}
    return wrapper


# ----------------------------------------------------------------------
# MCP TOOLS
# ----------------------------------------------------------------------

@mcp.tool("start_dht_monitoring",description="Starts DHT11 Sensor Monitoring for Temperatrue and Humidity")
def start_dht_monitoring(temp_threshold):
    print("Starting DHT Monitoring")
    return hardware.start_dht(temp_threshold)


@mcp.tool("stop_dht_monitoring",description="Stops DHT11 Sensor Monitoring")
def stop_dht_monitoring():
    return hardware.stop("dht")

@mcp.tool("start_motion_monitoring",description="Start Monitoring Motion Sensor")
def start_motion_monitoring():
    return hardware.start_motion()

@mcp.tool("stop_motion_monitoring",description="Stops Monitoring Motion Sensor")
def stop_motion_monitoring():
    return hardware.stop("motion")

@mcp.tool("start_light_monitoring",description="Starts Monitoring BH1750 Motion sensor for Light Intensity")
def start_light_monitoring():
    return hardware.start_light()

@mcp.tool("stop_light_monitoring",description="Stops Monitoring BH1750 Motion sensor for Light Intensity")
def stop_light_monitoring():
    return hardware.stop("light")

@mcp.tool("set_temp_threshold",description="Sets Temperature Threshold (default 30.0)")
def set_temp_threshold(value:float):
    return hardware.set_threshold(value)

@mcp.tool("get_buffers",description="Get Values of Sensors stored in the buffer")
def get_buffers():
    return hardware.buffers

@mcp.tool("system_status",description="Get The System Status")
def system_status():
    return hardware.system_status()

@mcp.tool("set_led",description="Set the RGB LED with given RGB values")
def mcp_set_led(green,blue,red):
    return hardware.set_led_manual(red,green,blue)

@mcp.tool("set_led_brightness",description="Set The Brightness of Given LED with Given brightness level")
def mcp_set_brightness(color,brightness):
    return hardware.set_led_brightness(color,brightness)

@mcp.tool("set_led_preset",description="Turn on the RGB led with given preset value")
def mcp_set_led_preset(preset):
    return hardware.set_led_preset(preset)

@mcp.tool("set_rgb_pattern",description="Start the RGB pattern of led for given time(seconds)")
def mcp_set_rgb_pattern(duration,color_interval:float=1):
    return hardware.RGB_Pattern(duration,color_interval)

@mcp.tool("stop_rgb_pattern",description="Turn on RGB pattern if any is currently active")
def mcp_stop_rgb_pattern():
    return hardware.stop_rgb_pattern()


@mcp.tool("blink_led",description="Blink The R|G|B Led N times given as parameters")
def mcp_blink_led(color:str,count:int=3,interval:float=0.3):
    print(f"Blinking {color} LED for {count} times with interval {interval} seconds")
    return hardware.blink_led(color,count,interval)