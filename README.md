# service.reactions

A Kodi service addon that reacts to system events (playback start/stop, screensaver on/off) by executing shell commands. 
This enables home automation workflows — control your lights, TV, air conditioning, or any external device directly from Kodi.

## Features

- **Playback reactions**: Execute commands when media starts or stops playing
- **Screensaver reactions**: Execute commands when the screensaver activates or deactivates
- **Hysteresis filtering**: Prevents false triggers from brief state changes
- **Live settings reload**: Change settings in the Kodi GUI without restarting the service
- **Debug logging**: Optional verbose logging for troubleshooting

## Installation

1. Download or clone this repository
2. Copy the `service.reactions` folder to your Kodi addons directory
3. Restart Kodi or enable the addon via *Settings → Add-ons → My add-ons → Services*

## Configuration

Open the addon settings via *Settings → Add-ons → My add-ons → Services → Reactions Service → Configure*.

### General

| Setting | Description |
|---|---|
| **Reaction: Start Playing** | Shell command to execute when media playback starts |
| **Reaction: Stop Playing** | Shell command to execute when media playback stops |
| **Reaction: Screensaver On** | Shell command to execute when the screensaver activates |
| **Reaction: Screensaver Off** | Shell command to execute when the screensaver deactivates |

### Pro-Settings

| Setting | Default | Description |
|---|---|---|
| **Service sleep time** | 5 seconds | Polling interval — how often the service checks for state changes |
| **Hysteresis** | 3 | Number of consecutive polls a state change must persist before triggering a command. Prevents false triggers from brief interruptions (e.g. buffering). Effective delay = sleep time × hysteresis |
| **Debug Mode** | Off | Enable verbose logging to the Kodi log file |

## Examples

### Home Assistant Integration

You can use `curl` commands to call Home Assistant REST API endpoints. This example presses an `input_button` entity when the screensaver activates or deactivates:

**Reaction: Screensaver On**
```bash
curl -X POST -H "Authorization: Bearer xxxxx.xxxxxx.xxxxx-xxxx-xxxx" -H "Content-Type: application/json" http://192.168.0.101:8123/api/services/input_button/press -d '{"entity_id": "input_button.button_sleepkodi_screensaver_goingactive"}'
```

**Reaction: Screensaver Off**
```bash
curl -X POST -H "Authorization: Bearer xxxxx.xxxxxx.xxxxx-xxxx-xxxx" -H "Content-Type: application/json" http://192.168.0.101:8123/api/services/input_button/press -d '{"entity_id": "input_button.button_sleepkodi_screensaver_goinginactive"}'
```

> **Note:** Replace `Bearer xxxxx.xxxxxx.xxxxx-xxxx-xxxx` with your actual [Home Assistant Long-Lived Access Token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) and adjust the entity IDs to match your setup.

### Simple Scripts

You can also call any local script or command:

```bash
/home/kodi/scripts/lights_on.sh
```

```bash
python3 /home/kodi/scripts/notify.py "Playback started"
```

## How It Works

The service polls Kodi's player and screensaver state at a configurable interval. To avoid false triggers (e.g. brief buffering pauses), a **hysteresis filter** requires the state change to persist for multiple consecutive polls before executing the configured command.

```
State change detected → Counter increments each poll
                      → Counter reaches hysteresis threshold → Command fires
State reverts early   → Counter resets to 0 (no command fired)
```

## License

[GPL-3.0](LICENSE)
