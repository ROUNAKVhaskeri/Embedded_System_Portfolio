import os,board,logging


GPIO_MOTION = 23
GPIO_DHT    = board.D4
GPIO_RGB_R  = 27
GPIO_RGB_G  = 22
GPIO_RGB_B  = 5

I2C_SCL     = board.SCL
I2C_SDA     = board.SDA

API_PORT    = 5000
API_HOST    = '0.0.0.0'

API_KEY     = "IoT202601POC"
MAX_BUFFER  = 300

SCHEMAS = {

    # ==================================================
    # LED — DIRECT CONTROL
    # ==================================================
    "set_led": {
        "type": "object",
        "properties": {
            "red":   {"type": "integer", "minimum": 0, "maximum": 255},
            "green": {"type": "integer", "minimum": 0, "maximum": 255},
            "blue":  {"type": "integer", "minimum": 0, "maximum": 255}
        },
        "required": ["red", "green", "blue"],
        "additionalProperties": False
    },

    "set_led_brightness": {
        "type": "object",
        "properties": {
            "color":{
                "type":"string",
                "enum":["red","green","blue","rgb"]
            },
            "brightness": {"type": "number", "minimum": 0, "maximum": 100}
        },
        "required": ["brightness"],
        "additionalProperties": False
    },

    "set_led_preset": {
        "type": "object",
        "properties": {
            "preset": {
                "type": "string",
                "enum": ["red","green","blue","white","yellow","cyan","magenta","orange","purple","pink","lime","teal","violet","indigo","brown","off"]
            }
        },
        "required": ["preset"],
        "additionalProperties": False
    },

    # ==================================================
    # LED — PATTERNS
    # ==================================================
    "set_rgb_pattern": {
        "type": "object",
        "properties": {
            "duration": {"type": "number", "minimum": 0.1, "maximum": 3600},
            "color_interval": {"type": "number", "minimum": 0.1, "maximum": 60}
        },
        "required": ["duration"],
        "additionalProperties": False
    },

    "stop_rgb_pattern": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "blink_led":{
        "type":"object",
        "properties":{
            "color":{
                "type": "string",
                "enum": ["red","green","blue","white","yellow","cyan","magenta","orange","purple","pink","lime","teal","violet","indigo","brown","off"]
            },
            "count":{"type":"integer","minimum":1,"maximum":100},
            "interval":{"type":"number","minimum":0.1,"maximum":10}
        },
        "additionalProperties":False,
        "required":["color"]
    },
    # ==================================================
    # SENSOR — ONE-SHOT READS (OPTIONAL)
    # ==================================================
    "read_temperature_humidity": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "read_light": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "read_motion": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    # ==================================================
    # SENSOR — PER-SENSOR MONITORING (CORE DESIGN)
    # ==================================================
    "start_dht_monitoring": {
        "type": "object",
        "properties": {
            "temp_threshold":{"type": "number", "minimum": 0, "maximum": 100}
        },
        "additionalProperties": False
    },

    "stop_dht_monitoring": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "start_light_monitoring": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "stop_light_monitoring": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "start_motion_monitoring": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "stop_motion_monitoring": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    # ==================================================
    # SYSTEM / MCP META
    # ==================================================
    "get_buffers": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "system_status": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    },

    "set_temp_threshold": {
        "type": "object",
        "properties": {
            "value": {"type": "number", "minimum": 0, "maximum": 100}
        },
        "required": ["value"],
        "additionalProperties": False
    }
}

AUTO_LIGHT_FLAGS = {
    "red":False,
    "green":False,
    "blue":False
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="./logs/log_file.log",
    filemode = "w"
)

logger = logging.getLogger("RPI_MCP")
