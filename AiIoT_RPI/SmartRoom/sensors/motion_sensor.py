import RPi.GPIO as GPIO
import time, threading

class MotionSensor:
    def __init__(self,pin) -> None:
        self.pin = pin
        self.motion_detected = False
        self.last_detection = 0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin,GPIO.IN)

    def read(self):
        with self._lock:
            current_state = GPIO.input(self.pin) == 1

            if current_state:
                self.last_detection = time.time()
                self.motion_detected = True
            else:
                if time.time() - self.last_detection > 5:
                    self.motion_detected = False
            
            return {
                "motion_detected":self.motion_detected,
                "raw_state":current_state,
                "last_detection":self.last_detection
                
            }
        
    def start_monitoring(self,callback = None):
        if self._running:
            return
        
        self._running = True
        def monitor_loop():
            previous_state = 0
            while self._running:
                current_state = GPIO.input(self.pin)

                if current_state == 1 and previous_state == 0:
                    with self._lock:
                        self.motion_detected = True
                        self.last_detection = time.time()
                    if callback:
                        callback(True)
                
                previous_state  = current_state

                with self._lock:
                    if self.motion_detected and time.time() - self.last_detection>5:
                        self.motion_detected = False
                        if callback:
                            callback(False)
                
                time.sleep(0.1)

        self._thread = threading.Thread(target=monitor_loop,daemon=True)
        self._thread.start()

    def stop_monitoring(self):
        """stop the monitoring thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        
    def cleanup(self):
        self.stop_monitoring()
        