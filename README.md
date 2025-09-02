# Solarmax to MQTT Agent

A Python application that polls a Solarmax inverter via socket connection, converts the response to comprehensive JSON format, and publishes it to an MQTT broker with **full Home Assistant integration**.

## ✨ Features

- **🏠 Home Assistant Ready**: Full auto-discovery support with proper device classes and units
- **⚡ Energy Dashboard Integration**: Automatically configured for HA Energy dashboard
- **📊 Comprehensive Data**: Valid JSON with parameter descriptions, converted and raw values
- **🔌 Three-Phase Support**: Adapted for three-phase Solarmax inverters (tested with 7TP2)
- **🛡️ Extensive Parameters**: Queries almost all available inverter values with automatic checksum and length calculation
- **🐍 Modern Python**: Compatible with Python 3.8+ with type hints and proper error handling
- **⚙️ Flexible Configuration**: Environment variables, JSON config files, or Home Assistant addon options
- **🔄 Robust Error Handling**: Continues operation without exiting on errors
- **🐳 Docker Support**: Ready-to-use Docker image, docker-compose setup, and Home Assistant addon
- **📝 Logging**: Comprehensive logging with configurable levels
- **💚 Health Monitoring**: Built-in health checks and availability status

## 🚀 Quick Start

### 🏠 Home Assistant Add-on (Recommended)

1. Add this repository to your Home Assistant add-on store
2. Install the "Solarmax to MQTT" add-on
3. Configure with your inverter IP and MQTT settings
4. Start the add-on
5. **All sensors automatically appear in Home Assistant!**

See [README_ADDON.md](README_ADDON.md) for detailed addon documentation.

### 🐳 Using Docker Compose

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```bash
   INVERTER_IP=192.168.1.100
   MQTT_BROKER_IP=192.168.1.10
   MQTT_INVERTER_TOPIC=homeassistant/sensor/solarmax
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

### Using Docker

```bash
docker build -t solarmax-agent .
docker run -d \
  --name solarmax-agent \
  -e INVERTER_IP=192.168.1.100 \
  -e MQTT_BROKER_IP=192.168.1.10 \
  -e MQTT_INVERTER_TOPIC=smarthome/solar/inverter \
  solarmax-agent
```

### Manual Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables and run:
   ```bash
   export INVERTER_IP=192.168.1.100
   export MQTT_BROKER_IP=192.168.1.10
   export MQTT_INVERTER_TOPIC=smarthome/solar/inverter
   python src/python/agent.py
   ```

## ⚙️ Configuration

All configuration is done via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INVERTER_IP` | ✅ | - | IP address of the Solarmax inverter |
| `INVERTER_PORT` | ❌ | 12345 | Port of the Solarmax inverter |
| `UPDATE_TIME` | ❌ | 5 | Update interval in seconds |
| `MQTT_BROKER_IP` | ✅ | - | IP address of the MQTT broker |
| `MQTT_BROKER_PORT` | ❌ | 1883 | Port of the MQTT broker |
| `MQTT_INVERTER_TOPIC` | ✅ | - | MQTT topic prefix for inverter data |
| `MQTT_BROKER_AUTH` | ❌ | - | JSON string with username/password |

### MQTT Authentication Example

```bash
MQTT_BROKER_AUTH='{"username": "your_user", "password": "your_pass"}'
```

## 📊 Data Format

The agent publishes data in two formats:

### Full Status Message
Published to: `{MQTT_INVERTER_TOPIC}/Full_Status`

```json
{
  "PAC": {
    "Value": 2500.0,
    "Description": "AC_Power (W)",
    "Raw Value": 5000
  },
  "SYS": {
    "Value": "In Betrieb",
    "Description": "status_Code",
    "Raw Value": 20001
  }
}
```

### Individual Parameters
Published to: `{MQTT_INVERTER_TOPIC}/{Description}_{Field}`

Example: `smarthome/solar/inverter/AC_Power (W)_(PAC)` → `2500.0`

## 🔧 Development

### Project Structure
```
├── src/python/agent.py    # Main application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── .env.example          # Environment template
└── README.md            # This file
```

### Code Quality
- Type hints throughout the codebase
- Comprehensive error handling and logging
- Object-oriented design with separation of concerns
- PEP 8 compliant code style

## 📋 Monitored Parameters

The agent monitors these inverter parameters:

**Energy Production:**
- Daily, Monthly, Yearly, and Total Energy
- DC and AC Power measurements
- String-specific power readings

**Electrical Measurements:**
- AC/DC Voltages and Currents
- Three-phase measurements (L1, L2, L3)
- String-specific measurements

**System Status:**
- Operating status and alarm codes
- Temperature monitoring
- Startup counters and operating hours

## 🔍 Troubleshooting

### Common Issues

1. **Cannot connect to inverter**
   - Verify `INVERTER_IP` and `INVERTER_PORT`
   - Check network connectivity
   - Ensure inverter supports socket connections

2. **MQTT publish failures**
   - Verify `MQTT_BROKER_IP` and `MQTT_BROKER_PORT`
   - Check authentication credentials
   - Ensure broker is accessible

3. **Invalid data parsing**
   - Check inverter model compatibility
   - Review logs for parsing errors
   - Verify inverter response format

### Logging

The application provides detailed logging. In Docker, view logs with:
```bash
docker logs solarmax-agent
```

## 📄 Dependencies

- **paho-mqtt**: MQTT client library (v2.1.0+)
- **Python**: 3.8 or higher

## 📜 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
