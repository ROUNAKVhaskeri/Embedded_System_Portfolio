import RPi.GPIO as GPIO
import time
import threading


class RGBled:
    def __init__(self,r_pin,g_pin,b_pin):
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(r_pin,GPIO.OUT)
        GPIO.setup(g_pin,GPIO.OUT)
        GPIO.setup(b_pin,GPIO.OUT)

        self.r_pwm = GPIO.PWM(r_pin,100)
        self.g_pwm = GPIO.PWM(g_pin,100)
        self.b_pwm = GPIO.PWM(b_pin,100)

        self.r_pwm.start(0)
        self.g_pwm.start(0)
        self.b_pwm.start(0)

        # Pattern control
        self.pattern_running = False
        self.pattern_thread = None

    def set_color(self,r,g,b):
        r_duty = 100 - (r*100/255)
        g_duty = 100 - (g*100/255)
        b_duty = 100 - (b*100/255)

        self.r_pwm.ChangeDutyCycle(r_duty)
        self.g_pwm.ChangeDutyCycle(g_duty)
        self.b_pwm.ChangeDutyCycle(b_duty)

        return {
            "status":"success",
            "color":{
                "r":r,
                "g":g,
                "b":b
            }
        }
    
    def rgb_pattern(self, duration=10, color_interval=0.3):
        """
        Run RGB cycling pattern for specified duration
        
        Args:
            duration: Total time to run pattern in seconds
            color_interval: Time each color stays on in seconds
        
        Returns:
            dict with status information
        """
        if self.pattern_running:
            return {
                "status": "error",
                "message": "Pattern already running"
            }
        
        def pattern_loop():
            try:
                self.pattern_running = True
                start_time = time.time()
                colors = [
                    (255, 0, 0),    # Red
                    (0, 255, 0),    # Green
                    (0, 0, 255)     # Blue
                ]
                color_index = 0
                
                while time.time() - start_time < duration:
                    r, g, b = colors[color_index % len(colors)]
                    self.set_color(r, g, b)
                    
                    # Wait for the interval or until duration expires
                    elapsed = time.time() - start_time
                    if elapsed + color_interval > duration:
                        time.sleep(duration - elapsed)
                    else:
                        time.sleep(color_interval)
                    
                    color_index += 1
                
                # Turn off LED after pattern completes
                self.set_color(0, 0, 0)
                self.pattern_running = False
                
            except Exception as e:
                self.set_color(0, 0, 0)
                self.pattern_running = False
                raise e
        
        # Start pattern in background thread
        self.pattern_thread = threading.Thread(target=pattern_loop, daemon=True)
        self.pattern_thread.start()
        
        return {
            "status": "success",
            "message": f"RGB pattern started for {duration} seconds",
            "color_interval": color_interval,
            "duration": duration
        }
    
    def stop_pattern(self):
        """Stop the current pattern and turn off LED"""
        self.pattern_running = False
        self.set_color(0, 0, 0)
        return {
            "status": "success",
            "message": "Pattern stopped"
        }
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop_pattern()
        self.r_pwm.stop()
        self.g_pwm.stop()
        self.b_pwm.stop()
        GPIO.cleanup([self.r_pin,self.g_pin,self.b_pin])