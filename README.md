# solarmax to mqtt agent

Python script which polls a solarmax inverter, converts the response to extensive JSON and publishes it to an mqtt broker.

Rewrite of the original to better fit my requirements.

Mostly based on the offical maxcom protocol description from Solarmax

## Features:
- Valid JSON with parameter description, converted and original Values.
- Adapted to work with three phase solarmax inverters (mine is an 7TP2)
- Should be able to query almost all available Values
  - Automatic checksum and length calculation 
- Compatible with Python 3+
- Parameters are set with environment variables
- Exception Handling without exiting
- Docker Image available



## dependencies

paho-mqtt  (https://pypi.org/project/paho-mqtt/)
