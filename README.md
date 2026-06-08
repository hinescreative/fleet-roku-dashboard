# Fleet Roku Dashboard

A simple setup to display a live "fleet status" dashboard (machines + Claude peers) on a Roku TV as an extended screen via Screen Mirroring / AirPlay.

## Goal
- Show status of fleet machines (Mac, PC, iMac, Clarvis, fleet-node, etc.) and online Claude peers (from claude-peers MCP mesh).
- One-click (double-click) to start.
- Clickable GUI for TV controls.
- Dashboard lives in browser on your Mac, mirrored to the big TV.

## Quick Start (Super Simple)
1. **Double-click** `Start-Fleet-Dashboard.command` (on Desktop or in this folder).
   - Starts local web server.
   - Preps the Roku TV (sends to Home, etc.).
2. Open the browser to the URL it provides (usually http://localhost:8080).
3. On your Mac: **Control Center → Screen Mirroring → select your Roku TV**.
4. Mirror the browser tab (or full screen) to the TV.

The dashboard should now be on the TV showing fleet machines and peers.

## Files / Structure
- `Start-Fleet-Dashboard.command` - The main "button". Double-click this.
- `scripts/`
  - `fleet` - Shell script that starts server + preps TV.
  - `fleet_gui.py` - Tkinter GUI with big clickable buttons (recommended for daily use).
  - `roku_ctl.py` - Low-level Roku control (ECP).
- `web/` - The actual dashboard (index.html). Edit this to customize what shows on TV.
- `roku-native/` - Optional native Roku channel starter (not used in current mirroring setup).
- `README.md`, `requirements.txt`

## Running the GUI (Click Buttons)
```bash
cd ~/Work/active-projects/fleet-roku-dashboard
python3 scripts/fleet_gui.py
```
This opens a window with buttons to start the dashboard, send keys to TV, launch apps, etc. No terminal typing needed after launch.

## Updating the Dashboard
Edit `web/index.html`. It's a self-contained HTML/JS page (uses Tailwind CDN).
Refresh the mirrored browser tab to see changes on TV.

Current content focuses on:
- Fleet machines (status, IPs, uptime, etc.)
- Claude peers online (with summaries from the mesh)

## TV Control
While dashboard is mirrored, you can still control the TV:
- Use the GUI buttons.
- Or from terminal (in project dir):
  ```bash
  python3 scripts/roku_ctl.py --ip 10.0.0.73 fleet
  python3 scripts/roku_ctl.py --ip 10.0.0.73 press Home
  python3 scripts/roku_ctl.py --ip 10.0.0.73 launch Plex
  ```

## Notes / Gotchas
- **Mirroring is manual** on the Mac side (Control Center). This is how Roku extended screen works.
- TV IP is currently hardcoded as `10.0.0.73` in scripts/. Update if it changes.
- Server runs on port 8080. Change if needed.
- Nothing is installed on the Roku itself — it's pure mirroring.
- The native channel in `roku-native/` is experimental (for future sideload instead of mirroring).
- Logs: `/tmp/fleet_dash.log`

## Resuming Later
1. Double-click `Start-Fleet-Dashboard.command` (or run the GUI).
2. Mirror as above.
3. Edit `web/index.html` for changes.

## Requirements
- macOS (for easy Screen Mirroring)
- Python 3 (Tkinter usually included)
- Roku TV on same network with Screen Mirroring enabled
- (Optional) `pip3 install -r requirements.txt` for better Roku lib

## GitHub
https://github.com/hinescreative/fleet-roku-dashboard

## To Do / Future
- Make IP configurable (env var or config file)
- Live polling for machine/peer status (instead of snapshot)
- Better error handling in GUI
- Auto-start server on login?
- Package as real macOS .app?

Created for easy fleet visibility on the big screen.
