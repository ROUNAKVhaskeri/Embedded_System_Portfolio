import requests, time
from datetime import datetime
from config import THINGSPEAK_API_KEY,THINGSPEAK_CHANNEL_ID,THINGSPEAK_BASE_URL
import thingspeak

class ThingspeakClient:
    def __init__(self) -> None:
        self.api_key = THINGSPEAK_API_KEY
        self.channel_id = THINGSPEAK_CHANNEL_ID
        self.base_url = THINGSPEAK_BASE_URL

    def send_data(self,temperature=None,humidity=None,lux=None):
        """Send Data to Thingspeak Cloud"""

        payload = {
            "api_key":THINGSPEAK_API_KEY,
            "field1":temperature,
            "field2":humidity,
            "field3":lux,
            "created_at":datetime.now().isoformat() + "Z"
        }
        
        try:
            response = requests.post(self.base_url,params=payload,timeout=15)

            if response.status_code == 200:
                return {
                    "success":True,
                    "entry_id":response.text
                }
            else:
                return {
                    "success":False,
                    "error":response.text
                }
        except requests.exceptions.Timeout:
            return {
                "success":False,
                "error":"Request timed out. Thingspeak server is not responding."
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success":False,
                "error":f"Connection failed: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success":False,
                "error":f"Request failed: {str(e)}"
            }
            