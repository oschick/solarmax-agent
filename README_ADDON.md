# Solarmax to MQTT - Home Assistant Add-on

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Connect your Solarmax inverter to Home Assistant via MQTT with automatic device discovery.

## About

This add-on connects to your Solarmax inverter via its built-in socket interface, reads comprehensive data, and publishes it to your MQTT broker with Home Assistant auto-discovery support. All sensors will automatically appear in your Home Assistant installation.

## Features

- 🏠 **Full Home Assistant Integration**: Automatic device and sensor discovery
- ⚡ **Comprehensive Data**: AC/DC power, voltage, current, energy totals, and system status
- 📊 **Energy Dashboard Ready**: Properly configured energy sensors for HA Energy dashboard
- 🔧 **Easy Setup**: Simple configuration through Home Assistant UI
- 📈 **Statistics Support**: Long-term statistics for all measurement sensors
- 🛡️ **Reliable**: Robust error handling and automatic reconnection
- 🔌 **MQTT Native**: Works with any MQTT broker (internal Mosquitto or external)

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Solarmax to MQTT" add-on
3. Configure the add-on (see configuration section below)
4. Start the add-on

## Configuration

### Basic Configuration

```yaml
inverter_ip: "192.168.1.100"      # IP address of your Solarmax inverter
inverter_port: 12345              # Port of your inverter (usually 12345)
update_interval: 30               # Update interval in seconds
mqtt_host: "core-mosquitto"       # MQTT broker (use "core-mosquitto" for HA internal broker)
mqtt_port: 1883                   # MQTT port
device_name: "Solarmax Inverter"  # Device name in Home Assistant
```

### Advanced Configuration

```yaml
mqtt_username: "your_mqtt_user"   # MQTT username (if required)
mqtt_password: "your_mqtt_pass"   # MQTT password (if required)
device_id: "solarmax_inverter"    # Unique device ID
home_assistant_discovery: true    # Enable HA auto-discovery
discovery_prefix: "homeassistant" # HA discovery prefix
mqtt_topic_prefix: "solarmax"     # MQTT topic prefix
log_level: "INFO"                 # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## Home Assistant Integration

### Automatic Discovery

When enabled (default), the add-on will automatically create all sensors in Home Assistant:

- **Power Sensors**: AC Power, DC Power, String Powers
- **Energy Sensors**: Daily, Monthly, Yearly, and Total Energy
- **Electrical Sensors**: Voltages and Currents for all phases
- **Status Sensors**: System status and alarm codes
- **Temperature Sensor**: Inverter operating temperature

### Energy Dashboard

The following sensors are automatically configured for the Home Assistant Energy Dashboard:

- `sensor.solarmax_inverter_kt0` (Total Energy) - Main energy production sensor
- `sensor.solarmax_inverter_kdy` (Daily Energy) - Daily production
- `sensor.solarmax_inverter_pac` (AC Power) - Current power production

### Device Information

All sensors are grouped under a single device with:
- Manufacturer: Solarmax
- Model: Inverter
- Device Name: Configurable (default: "Solarmax Inverter")

## Monitored Data

### Power Production
- AC Power (W)
- DC Power Total (W)
- DC Power String 1 (W)
- DC Power String 2 (W)

### Energy Production
- Energy Day (Wh)
- Energy Month (kWh)
- Energy Year (kWh)
- Energy Total (kWh)

### Electrical Measurements
- AC Voltage L1/L2/L3 (V)
- AC Current L1/L2/L3 (A)
- DC Voltage String 1/2 (V)
- DC Current String 1/2 (A)

### System Information
- System Status
- Alarm Codes
- Operating Temperature (°C)
- Power-on Hours
- Startup Count

## Troubleshooting

### Add-on Won't Start

1. Check the configuration for correct inverter IP and port
2. Ensure your inverter supports socket communication (port 12345)
3. Verify network connectivity between Home Assistant and inverter

### No Sensors Appearing

1. Ensure MQTT broker is running and accessible
2. Check MQTT credentials if using authentication
3. Verify Home Assistant MQTT integration is configured
4. Check add-on logs for connection errors

### Inverter Connection Issues

1. Verify inverter IP address and port
2. Check if inverter web interface is accessible
3. Some inverters may need to be configured to enable socket communication
4. Ensure no firewall is blocking the connection

### MQTT Issues

1. For internal broker: Ensure Mosquitto add-on is installed and running
2. For external broker: Verify host, port, and credentials
3. Check MQTT integration configuration in Home Assistant

## Support

If you have issues with this add-on, please check the logs and create an issue on the GitHub repository.

## Changelog

### 1.0.0
- Initial release
- Home Assistant auto-discovery support
- Energy dashboard integration
- Comprehensive sensor coverage
- Robust error handling

---

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
