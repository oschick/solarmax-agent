#!/usr/bin/with-contenv bashio

# Print startup banner
bashio::log.info "Starting Solarmax to MQTT Agent..."

# Set log level from addon options
export LOG_LEVEL=$(bashio::config 'log_level')

# Check if MQTT service is available
if bashio::services.available "mqtt"; then
    bashio::log.info "MQTT service available, using internal broker"
else
    bashio::log.info "Using external MQTT broker"
fi

# Start the Python application
exec python3 /app/agent.py
