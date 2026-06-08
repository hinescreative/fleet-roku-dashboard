# Fleet Roku Dashboard

Simple one-click (or one double-click) setup to display a live fleet status dashboard on your Roku TV as an extended screen.

## What it shows
- Fleet machines (Mac, PC, iMac, Clarvis, fleet-node, etc.) with status, Tailscale IPs, uptime, load, etc.
- Online Claude peers from the mesh (with machine, CWD, and current summary of what each peer is working on).

## Super simple usage (no terminal after first setup)

1. **Double-click** `Start-Fleet-Dashboard.command` on your Desktop (or in this folder).
   - This starts the local web server and preps the Roku TV.
2. Open the browser page it gives you (http://localhost:8080).
3. On your Mac: Control Center → Screen Mirroring → select your Roku TV.
4. Mirror the tab (or full screen). The fleet/peers dashboard appears on the TV.

## Bonus: Clickable GUI
Run `python3 fleet_gui.py` (or double-click the Desktop command) to get a window with big buttons for:
- Starting the dashboard
- Sending Home, launching Plex/YouTube, switching inputs (Xbox etc.), volume, status, etc.

## Files
- `fleet` – main shell launcher
- `fleet_gui.py` – Tkinter GUI with clickable buttons (no terminal needed for daily use)
- `fleet-dashboard-web/` – the actual dashboard HTML (fleet machines + peers view)
- `roku_ctl.py` – Roku ECP control script
- `fleet-dashboard/` – optional native Roku channel starter (if you ever want to sideload instead of mirroring)
- `Start-Fleet-Dashboard.command` – the Desktop "button" (double-click this)

## Requirements
- macOS (the mirroring part)
- Python 3 (with tkinter, usually included)
- Your Roku TV on the same network with Screen Mirroring enabled
- (Optional) The `roku` Python package for nicer control: `pip3 install -r requirements.txt`

## How to update the dashboard
Edit `fleet-dashboard-web/index.html` (it's just HTML/JS with Tailwind). Refresh the mirrored tab.

## TV controls from the GUI or script
While the dashboard is mirrored you can still control the TV:
- Use the GUI buttons
- Or from terminal: `python3 roku_ctl.py --ip YOUR_ROKU_IP fleet --cast`

## Notes
- This uses local web serving + Mac Screen Mirroring / AirPlay. Nothing is installed on the Roku itself.
- The native channel folder is included for future experiments but the mirroring route is currently the simplest.

Created for Wes's fleet monitoring on the big screen.
