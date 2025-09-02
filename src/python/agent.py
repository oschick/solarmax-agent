# coding=utf-8
"""
Solarmax Inverter to MQTT Agent for Home Assistant

This agent reads data from a Solarmax inverter via socket connection,
converts the response to JSON format, and publishes it to an MQTT broker
with Home Assistant auto-discovery support.
"""

import json
import logging
import socket
import time
from datetime import datetime
from os import environ, path
from typing import Any, Dict, Optional, Union

import paho.mqtt.client as mqtt

# Configure logging for Home Assistant addon compatibility
log_level = environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("solarmax-agent")

# Home Assistant addon configuration paths
CONFIG_PATH = "/data/options.json"
HASSIO_CONFIG_PATH = "/config/solarmax-agent.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from Home Assistant addon or environment variables."""
    config = {}

    # Try Home Assistant addon configuration first
    if path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            logger.info("Loaded configuration from Home Assistant addon")
        except Exception as e:
            logger.warning(f"Failed to load addon config: {e}")

    # Try alternative config path
    elif path.exists(HASSIO_CONFIG_PATH):
        try:
            with open(HASSIO_CONFIG_PATH, "r") as f:
                config = json.load(f)
            logger.info("Loaded configuration from /config/solarmax-agent.json")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")

    # Fallback to environment variables with Home Assistant defaults
    return {
        "inverter_ip": config.get("inverter_ip") or environ.get("INVERTER_IP"),
        "inverter_port": config.get("inverter_port")
        or int(environ.get("INVERTER_PORT", "12345")),
        "update_interval": config.get("update_interval")
        or int(environ.get("UPDATE_TIME", "30")),
        "mqtt_host": config.get("mqtt_host")
        or environ.get("MQTT_BROKER_IP", "core-mosquitto"),
        "mqtt_port": config.get("mqtt_port")
        or int(environ.get("MQTT_BROKER_PORT", "1883")),
        "mqtt_username": config.get("mqtt_username") or environ.get("MQTT_USERNAME"),
        "mqtt_password": config.get("mqtt_password") or environ.get("MQTT_PASSWORD"),
        "mqtt_topic_prefix": config.get("mqtt_topic_prefix")
        or environ.get("MQTT_INVERTER_TOPIC", "homeassistant/sensor/solarmax"),
        "device_name": config.get("device_name", "Solarmax Inverter"),
        "device_id": config.get("device_id", "solarmax_inverter"),
        "home_assistant_discovery": config.get("home_assistant_discovery", True),
        "discovery_prefix": config.get("discovery_prefix", "homeassistant"),
        "availability_topic": config.get(
            "availability_topic", "homeassistant/sensor/solarmax/availability"
        ),
    }


# Load configuration
CONFIG = load_config()

# Validate required configuration
if not all([CONFIG["inverter_ip"], CONFIG["mqtt_host"]]):
    logger.error("Missing required configuration: inverter_ip, mqtt_host")
    exit(1)

logger.info(
    f"Starting Solarmax Agent with config: "
    f"inverter={CONFIG['inverter_ip']}:{CONFIG['inverter_port']}, "
    f"mqtt={CONFIG['mqtt_host']}:{CONFIG['mqtt_port']}"
)


# PAC = "PAC" # AC power (W)
# PD01 = "PD01" # DC Power String 1 (W)
# PD02 = "PD02" # DC Power String 2 (W)
# PDC = "PDC" # DC Power (W)
# PDA = "PDA" # ????

# QAC = "QAC" # ????
# SAC = "SAC" # ????
# TKK = "TKK" # ????
# TNF = "TNF" # AC Freq (Hz)
# TYP = "TYP" # Type
# SWV = "SWV" # Software Version
# CAC = "CAC" # Start ups

# "DYR": "Year",
# "DMT": "Month",
# "DDY": "Day",
# "THR": "Hour",
# "TMI": "Minute",

# "TYP": "Type",


# KHR = "KHR" # poweronhours
# KYR = "KYR" # Energy year (kwh)
# KLY = "KLY" # energy Last year (kwh)
# KMT = "KMT" # Energy month (kwh)
# KLM = "KLM" # Energy last month (kwh)
# KDY = "KDY" # Energy day (wh)
# KLD = "KLD" # Energy yesterday (kwh)
# KT0 = "KT0" # Energy Total (kwh)
# PIN = "PIN" # Installed power (W)
# ADR = "ADR" # Adress
# PRL = "PRL" # relative Power %
# UDC = "UDC" # DC Voltage (mv)
# UD01 = "UD01" # DC Voltage String 1 (mv)
# UD02 = "UD02" # DC Voltage String 2 (mv)

# UI1 = "UI1" # ????
# UI2 = "UI2" # ????
# UI3 = "UI3" # ????

# UM1 = "UM1" # Uac 10m L1
# UM2 = "UM2" # Uac 10m L2
# UM3 = "UM3" # Uac 10m L3


# UL1 = "UL1" # AC Voltage Phase 1
# UL2 = "UL2" # AC Voltage Phase 2
# UL3 = "UL3" # AC Voltage Phase 3
# IDC = "IDC" # DC Current
# ID01 = "ID01" # DC Current String 1
# ID02 = "ID02" # DC Current String 2
# IED = "IED" # Ierr DC Fehlerstrom
# IEE = "IEE" # Ierr AC Fehlerstrom

# IL1 = "IL1" # AC Current Phase 1
# IL2 = "IL2" # AC Current Phase 2
# IL3 = "IL3" # AC Current Phase 3
# IML1 = "IML1" # Iac mean L1
# IML2 = "IML2" # Iac mean L2
# IML3 = "IML3" # Iac mean L3
# PAM = "PAM" # ????
# SAL = "SAL" # Alarm Codes
# SYS = "SYS" # status code


# Solarmax status codes
STATUS_CODES = {
    20000: "Keine Kommunikation",
    20001: "In Betrieb",
    20002: "Zu wenig Einstrahlung",
    20003: "Anfahren",
    20004: "Betrieb auf MPP",
    20005: "Ventilator laeuft",
    20006: "Betrieb auf Maximalleistung",
    20007: "Temperaturbegrenzung",
    20008: "Netzbetrieb",
}

# Solarmax alarm codes
ALARM_CODES = {
    0: "kein Fehler",
    1: "Externer Fehler 1",
    2: "Isolationsfehler DC-Seite",
    4: "Fehlerstrom Erde zu Groß",
    8: "Sicherungsbruch Mittelpunkterde",
    16: "Externer Alarm 2",
    32: "Langzeit-Temperaturbegrenzung",
    64: "Fehler AC-Einspeisung",
    128: "Externer Alarm 4",
    256: "Ventilator defekt",
    512: "Sicherungsbruch",
    1024: "Ausfall Temperatursensor",
    2048: "Alarm 12",
    4096: "Alarm 13",
    8192: "Alarm 14",
    16384: "Alarm 15",
    32768: "Alarm 16",
    65536: "Alarm 17",
}

# Home Assistant device class mappings for better integration
DEVICE_CLASSES = {
    "PAC": "power",
    "PDC": "power",
    "PD01": "power",
    "PD02": "power",
    "UL1": "voltage",
    "UL2": "voltage",
    "UL3": "voltage",
    "UD01": "voltage",
    "UD02": "voltage",
    "IL1": "current",
    "IL2": "current",
    "IL3": "current",
    "IDC": "current",
    "ID01": "current",
    "ID02": "current",
    "KDY": "energy",
    "KMT": "energy",
    "KYR": "energy",
    "KT0": "energy",
    "TKK": "temperature",
    "KHR": None,  # No specific device class for hours
    "CAC": None,  # No device class for counters
}

# Units of measurement for Home Assistant
UNITS_OF_MEASUREMENT = {
    "PAC": "W",
    "PDC": "W",
    "PD01": "W",
    "PD02": "W",
    "UL1": "V",
    "UL2": "V",
    "UL3": "V",
    "UD01": "V",
    "UD02": "V",
    "IL1": "A",
    "IL2": "A",
    "IL3": "A",
    "IDC": "A",
    "ID01": "A",
    "ID02": "A",
    "KDY": "Wh",
    "KMT": "kWh",
    "KYR": "kWh",
    "KT0": "kWh",
    "TKK": "°C",
    "KHR": "h",
    "CAC": "",
    "SAL": "",
    "SYS": "",
}

# State classes for Home Assistant (for statistics and energy dashboard)
STATE_CLASSES = {
    "PAC": "measurement",
    "PDC": "measurement",
    "PD01": "measurement",
    "PD02": "measurement",
    "UL1": "measurement",
    "UL2": "measurement",
    "UL3": "measurement",
    "UD01": "measurement",
    "UD02": "measurement",
    "IL1": "measurement",
    "IL2": "measurement",
    "IL3": "measurement",
    "IDC": "measurement",
    "ID01": "measurement",
    "ID02": "measurement",
    "KDY": "total_increasing",
    "KMT": "total_increasing",
    "KYR": "total_increasing",
    "KT0": "total_increasing",
    "TKK": "measurement",
    "KHR": "total_increasing",
    "CAC": "total_increasing",
}

# Field mapping for inverter parameters
FIELD_MAP_INVERTER = {
    "KDY": "Energy_Day (Wh)",
    "KMT": "Energy_Month (kWh)",
    "KYR": "Energy_Year (kWh)",
    "KT0": "Energy_Total (kWh)",
    "PDC": "DC_Power (W)",
    "PD01": "DC_Power_String_1 (W)",
    "PD02": "DC_Power_String_2 (W)",
    "UD01": "DC_Voltage_String_1 (V)",
    "UD02": "DC_Voltage_String_2 (V)",
    "IDC": "DC_Current (A)",
    "ID01": "DC_Current_String_1 (A)",
    "ID02": "DC_Current_String_2 (A)",
    "PAC": "AC_Power (W)",
    "UL1": "AC_Voltage_Phase_1 (V)",
    "UL2": "AC_Voltage_Phase_2 (V)",
    "UL3": "AC_Voltage_Phase_3 (V)",
    "IL1": "AC_Current_Phase_1 (A)",
    "IL2": "AC_Current_Phase_2 (A)",
    "IL3": "AC_Current_Phase_3 (A)",
    "CAC": "Startups",
    "KHR": "poweronhours",
    "TKK": "inverter_operating_temp (C)",
    "SAL": "Alarm_Codes",
    "SYS": "status_Code",
}

# Base request template
REQUEST_TEMPLATE = "{FB;01;!!|64:&&|$$$$}"


def build_request(field_map: Dict[str, str]) -> str:
    """Build the request message for the inverter."""
    fields = ";".join(field_map.keys())
    req = REQUEST_TEMPLATE.replace("&&", fields)
    # Replace !! with length of string in 2-digit hex
    req = req.replace("!!", format(len(req), "02X"))
    # Replace $$$$ with checksum
    req = req.replace("$$$$", calculate_checksum((req[1:])[:-5]))
    return req


def calculate_checksum(data: str) -> str:
    """Calculate the checksum for the message."""
    checksum_value = sum(ord(c) for c in data)
    logger.debug(f"Checksum calculation for '{data}': {checksum_value}")
    return format(checksum_value, "04X")


def map_data_value(field: str, value: int) -> Union[str, float, int]:
    """Convert raw inverter values to useful units."""
    if field == "SYS":
        return STATUS_CODES.get(value, "Unknown Status Code")
    elif field == "SAL":
        return ALARM_CODES.get(value, "Unknown Alarm Code")
    elif field in ["PAC", "PD01", "PD02", "PDC"]:
        return value / 2
    elif field in ["UL1", "UL2", "UL3", "UDC", "UD01", "UD02"]:
        return value / 10.0
    elif field in ["IDC", "ID01", "ID02", "IL1", "IL2", "IL3"]:
        return value / 100.0
    else:
        return value


class HomeAssistantMQTTPublisher:
    """MQTT Publisher with Home Assistant auto-discovery support."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client: Optional[mqtt.Client] = None
        self.discovery_sent = False

    def _create_client(self) -> mqtt.Client:
        """Create and configure MQTT client."""
        client = mqtt.Client(client_id=f"solarmax_{self.config['device_id']}")

        if self.config.get("mqtt_username") and self.config.get("mqtt_password"):
            client.username_pw_set(
                username=self.config["mqtt_username"],
                password=self.config["mqtt_password"],
            )

        # Set up callbacks for better debugging
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_publish = self._on_publish

        return client

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the MQTT broker."""
        if rc == 0:
            logger.info("Successfully connected to MQTT broker")
            # Publish availability
            self._publish_availability("online")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the MQTT broker."""
        logger.warning(f"Disconnected from MQTT broker with code {rc}")

    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        logger.debug(f"Message {mid} published successfully")

    def _publish_availability(self, status: str):
        """Publish availability status for Home Assistant."""
        if self.client:
            self.client.publish(self.config["availability_topic"], status, retain=True)

    def _send_discovery_config(self, field: str, field_data: Dict[str, Any]):
        """Send Home Assistant discovery configuration for a sensor."""
        if not self.config.get("home_assistant_discovery", True):
            return

        sensor_name = f"{self.config['device_name']} {field}"
        unique_id = f"{self.config['device_id']}_{field.lower()}"

        # Create discovery topic
        discovery_topic = (
            f"{self.config['discovery_prefix']}/sensor/"
            f"{self.config['device_id']}/{field.lower()}/config"
        )

        # Create discovery payload
        discovery_payload = {
            "name": sensor_name,
            "unique_id": unique_id,
            "state_topic": f"{self.config['mqtt_topic_prefix']}/{field}",
            "availability_topic": self.config["availability_topic"],
            "device": {
                "identifiers": [self.config["device_id"]],
                "name": self.config["device_name"],
                "manufacturer": "Solarmax",
                "model": "Inverter",
                "sw_version": "1.0.0",
            },
            "json_attributes_topic": f"{self.config['mqtt_topic_prefix']}/attributes",
        }

        # Add device class if available
        if field in DEVICE_CLASSES and DEVICE_CLASSES[field]:
            discovery_payload["device_class"] = DEVICE_CLASSES[field]

        # Add unit of measurement
        if field in UNITS_OF_MEASUREMENT and UNITS_OF_MEASUREMENT[field]:
            discovery_payload["unit_of_measurement"] = UNITS_OF_MEASUREMENT[field]

        # Add state class for statistics
        if field in STATE_CLASSES:
            discovery_payload["state_class"] = STATE_CLASSES[field]

        # Special handling for energy sensors (for Energy dashboard)
        if field in ["KDY", "KMT", "KYR", "KT0"]:
            discovery_payload["icon"] = "mdi:solar-power"
            if field == "KT0":  # Total energy - important for energy dashboard
                discovery_payload["last_reset_topic"] = (
                    f"{self.config['mqtt_topic_prefix']}/last_reset"
                )

        # Special handling for power sensors
        if field in ["PAC", "PDC", "PD01", "PD02"]:
            discovery_payload["icon"] = "mdi:solar-power"

        # Special handling for status sensors
        if field in ["SYS", "SAL"]:
            discovery_payload["icon"] = "mdi:information"

        if self.client:
            self.client.publish(
                discovery_topic, json.dumps(discovery_payload), retain=True
            )
            logger.debug(f"Sent discovery config for {sensor_name}")

    def publish_data(self, data: Dict[str, Any]) -> bool:
        """Publish the data to MQTT broker with Home Assistant support."""
        try:
            if not self.client:
                self.client = self._create_client()
                self.client.connect(
                    self.config["mqtt_host"], self.config["mqtt_port"], 60
                )
                self.client.loop_start()
                time.sleep(1)  # Give connection time to establish

            # At this point, self.client is guaranteed to be not None
            if self.client is None:
                raise RuntimeError("MQTT client failed to initialize")

            # Send discovery configs on first run
            if not self.discovery_sent and self.config.get(
                "home_assistant_discovery", True
            ):
                for field in data.keys():
                    self._send_discovery_config(field, data[field])
                self.discovery_sent = True
                logger.info("Sent Home Assistant discovery configurations")

            # Publish individual sensor values
            for field, field_data in data.items():
                topic = f"{self.config['mqtt_topic_prefix']}/{field}"
                value = field_data.get("Value", 0)
                self.client.publish(topic, str(value), retain=True)

            # Publish full data as attributes
            attributes_topic = f"{self.config['mqtt_topic_prefix']}/attributes"
            self.client.publish(attributes_topic, json.dumps(data), retain=True)

            # Update availability
            self._publish_availability("online")

            logger.info(f"Published data for {len(data)} sensors")
            return True

        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {e}")
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
                self.client = None
            return False

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client:
            self._publish_availability("offline")
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None


def convert_to_json(field_map: Dict[str, str], data: str) -> Dict[str, Any]:
    """Convert inverter response to JSON format."""
    # Example data:
    # b'{01;FB;EA|64:PAC=1F0A;PD01=CB2;PD02=13BA;PDC=206C;CAC=CAF;...}'
    try:
        data_split = data.split(":")[1].split("|")[0].split(";")
        result_dict = {}

        for item in data_split:
            if "=" not in item:
                continue

            field, value_str = item.split("=", 1)

            if field == "SYS":
                # Cut off the ",0" in SYS status
                value = int(value_str.split(",")[0], 16)
            else:
                value = int(value_str, 16)

            result_dict[field] = {
                "Value": map_data_value(field, value),
                "Description": field_map[field],
                "Raw Value": value,
            }

        logger.debug(f"Converted data: {result_dict}")
        return result_dict

    except Exception as e:
        logger.error(f"Error converting data to JSON: {e}")
        return {}


class InverterConnection:
    """Handles socket connection to the Solarmax inverter."""

    def __init__(self, ip: str, port: int, timeout: int = 10):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def connect(self) -> Optional[socket.socket]:
        """Establish connection to the inverter."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, self.port))
            logger.info(f"Connected to inverter at {self.ip}:{self.port}")
            return sock
        except socket.error as e:
            logger.error(f"Failed to connect to inverter: {e}")
            return None

    def read_data(self, sock: socket.socket, request: str) -> str:
        """Send request and read response from inverter."""
        try:
            logger.info(f"Sending request: {request}")
            sock.send(bytes(request, "utf-8"))

            response = ""
            start_time = datetime.now()
            data_received = False

            while (
                not data_received and (datetime.now() - start_time).total_seconds() < 2
            ):
                buf = sock.recv(1024)
                if len(buf) > 0:
                    response += buf.decode("utf-8", errors="ignore")
                    data_received = True

            logger.info(f"Received response: {response}")
            return response

        except Exception as e:
            logger.error(f"Error reading data from inverter: {e}")
            return ""


def generate_empty_data(
    field_map: Dict[str, str], last_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate empty/default data when inverter is not available."""
    if last_data:
        # Update last known data with offline status
        data = last_data.copy()
        for field in data:
            if field in ["KDY", "KMT", "KYR", "KT0", "KHR", "CAC"]:
                continue  # Keep energy/counter values
            elif field == "SYS":
                data[field]["Value"] = map_data_value(field, 20000)
            else:
                data[field]["Raw Value"] = 0
                data[field]["Value"] = map_data_value(field, 0)
        return data
    else:
        # Generate fresh empty data
        data = {}
        for field in field_map:
            if field == "SYS":
                data[field] = {
                    "Value": "Keine Kommunikation",
                    "Description": field_map[field],
                    "Raw Value": 20000,
                }
            else:
                data[field] = {
                    "Value": 0,
                    "Description": field_map[field],
                    "Raw Value": 0,
                }
        return data


def main():
    """Main function to run the inverter monitoring agent."""
    logger.info("Starting Solarmax to MQTT Agent for Home Assistant...")

    # Initialize components with config
    inverter = InverterConnection(CONFIG["inverter_ip"], CONFIG["inverter_port"])
    mqtt_publisher = HomeAssistantMQTTPublisher(CONFIG)

    # Build request for inverter
    request_message = build_request(FIELD_MAP_INVERTER)
    last_good_data = {}

    # Set up signal handler for graceful shutdown
    import signal

    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, cleaning up...")
        mqtt_publisher.disconnect()
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            # Try to connect to inverter
            connection = inverter.connect()

            if connection:
                # Read data from inverter
                raw_data = inverter.read_data(connection, request_message)
                json_data = convert_to_json(FIELD_MAP_INVERTER, raw_data)

                if json_data:  # Only publish if we got valid data
                    mqtt_publisher.publish_data(json_data)
                    last_good_data = json_data
                    sleep_time = CONFIG["update_interval"]
                else:
                    logger.warning("No valid data received from inverter")
                    sleep_time = 60  # Wait longer on data errors

                connection.close()
            else:
                # Inverter not available, publish empty/last known data
                logger.warning("Inverter not available, publishing offline status")
                if last_good_data:
                    json_data = generate_empty_data(FIELD_MAP_INVERTER, last_good_data)
                else:
                    json_data = generate_empty_data(FIELD_MAP_INVERTER)

                mqtt_publisher.publish_data(json_data)
                sleep_time = 60  # Wait longer when inverter is offline

            logger.debug(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
            mqtt_publisher.disconnect()
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            time.sleep(60)  # Wait before retrying on errors
            continue


if __name__ == "__main__":
    main()
