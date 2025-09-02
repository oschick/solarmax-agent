---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''

---

## Bug Description
A clear and concise description of what the bug is.

## Environment
- **Deployment Type**: [Home Assistant Addon / Docker / Manual]
- **Home Assistant Version**: [if using addon]
- **Agent Version**: [version or commit hash]
- **Architecture**: [amd64, arm64, armv7, etc.]
- **Solarmax Inverter Model**: [e.g., SolarMax 7TP2]

## Configuration
```json
// Paste your configuration here (remove sensitive data like passwords)
{
  "inverter_ip": "192.168.x.x",
  "mqtt_host": "...",
  // ... other config
}
```

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Steps to Reproduce
1. Configure agent with...
2. Start the service...
3. Observe...
4. See error

## Logs
```
Paste relevant log output here. For Home Assistant addon, check the addon logs.
For Docker: docker logs [container-name]
```

## MQTT Messages
If applicable, paste MQTT messages you're seeing (or not seeing):
```
Topic: homeassistant/sensor/solarmax/PAC
Payload: 1234.5
```

## Home Assistant Integration
If using with Home Assistant:
- [ ] Sensors appear in Home Assistant
- [ ] Discovery messages are sent
- [ ] Energy dashboard integration works
- [ ] Device information is correct

## Additional Context
Add any other context about the problem here, such as:
- Network setup (VLANs, firewalls, etc.)
- Recent changes to configuration
- Screenshots of Home Assistant UI
- Inverter web interface screenshots
