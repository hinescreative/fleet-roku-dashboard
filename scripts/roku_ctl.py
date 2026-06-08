#!/usr/bin/env python3
"""
Roku Control Toolkit / Playground
Zero-dependency core (uses only stdlib urllib). Optional 'roku' library for nicer app handling.

Usage examples:
  python3 roku_ctl.py --ip 192.168.1.42 status
  python3 roku_ctl.py --ip 192.168.1.42 press Home
  python3 roku_ctl.py --ip 192.168.1.42 press Select
  python3 roku_ctl.py --ip 192.168.1.42 apps
  python3 roku_ctl.py --ip 192.168.1.42 launch Netflix
  python3 roku_ctl.py --ip 192.168.1.42 interactive

Add your own macros in the MACROS dict below.
"""

import argparse
import sys
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict

# =============================================================================
# Low-level ECP (works with nothing but Python stdlib)
# =============================================================================

def _post(ip: str, path: str, data: bytes = b"") -> None:
    url = f"http://{ip}:8060{path}"
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        urllib.request.urlopen(req, timeout=6)
    except Exception as e:
        print(f"Error sending to {url}: {e}", file=sys.stderr)

def _get(ip: str, path: str) -> bytes:
    url = f"http://{ip}:8060{path}"
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            return resp.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return b""

def send_key(ip: str, key: str) -> None:
    """Send a keypress. Works for Home, Select, Play, VolumeUp, PowerOn, letters, etc."""
    _post(ip, f"/keypress/{key}")

def send_keydown(ip: str, key: str) -> None:
    _post(ip, f"/keydown/{key}")

def send_keyup(ip: str, key: str) -> None:
    _post(ip, f"/keyup/{key}")

def launch_app(ip: str, app_id: str) -> None:
    """Launch by numeric app ID (get IDs from 'apps' command)."""
    _post(ip, f"/launch/{app_id}")

def input_command(ip: str, params: Dict[str, str]) -> None:
    """For deep links / transport controls etc. Example params: {'id': '123', 'type': 'tune'}"""
    qs = urllib.parse.urlencode(params)
    _post(ip, f"/input?{qs}")

def get_device_info(ip: str) -> Dict[str, str]:
    data = _get(ip, "/query/device-info")
    if not data:
        return {}
    root = ET.fromstring(data)
    return {child.tag: (child.text or "").strip() for child in root}

def get_active_app(ip: str) -> Dict[str, str]:
    data = _get(ip, "/query/active-app")
    if not data:
        return {}
    root = ET.fromstring(data)
    app = root.find("app")
    if app is not None:
        return {
            "id": app.get("id", ""),
            "type": app.get("type", ""),
            "version": app.get("version", ""),
            "name": (app.text or "").strip(),
        }
    return {}

def get_media_player(ip: str) -> Dict[str, str]:
    data = _get(ip, "/query/media-player")
    if not data:
        return {}
    root = ET.fromstring(data)
    player = root.find("player")
    if player is not None:
        return {k: (v or "").strip() for k, v in player.attrib.items()}
    return {}

def get_apps(ip: str) -> List[Dict[str, str]]:
    data = _get(ip, "/query/apps")
    if not data:
        return []
    root = ET.fromstring(data)
    apps = []
    for app in root.findall("app"):
        apps.append({
            "id": app.get("id", ""),
            "type": app.get("type", ""),
            "version": app.get("version", ""),
            "name": (app.text or "").strip(),
        })
    return apps

# =============================================================================
# Optional high-level wrapper (if 'roku' library is installed)
# =============================================================================

def get_roku(ip: str):
    try:
        from roku import Roku
        return Roku(ip)
    except ImportError:
        return None

# =============================================================================
# Macros & Scenes (easy to extend)
# =============================================================================

MACROS: Dict[str, List[str]] = {
    "home": ["Home"],
    "movie_night": ["Home", "Select", "Down", "Down", "Select"],  # tweak for your layout
    "bedtime": ["Home", "PowerOff"],
    "volume_up": ["VolumeUp"],
    "volume_down": ["VolumeDown"],
    "mute": ["Mute"],
    "play_pause": ["Play"],
    # Grey area fun ones for your setup (use with launch or extend)
    # "xbox": switch to HDMI2 input + whatever
    # "plex_party": launch Plex etc.
}

def run_macro(ip: str, name: str) -> None:
    keys = MACROS.get(name.lower())
    if not keys:
        print(f"Unknown macro: {name}. Available: {', '.join(MACROS.keys())}")
        return
    print(f"Running macro: {name}")
    for k in keys:
        send_key(ip, k)
        time.sleep(0.25)
    print("Done.")

# =============================================================================
# CLI
# =============================================================================

def print_status(ip: str) -> None:
    print("=== Device Info ===")
    info = get_device_info(ip)
    for k, v in sorted(info.items()):
        if v:
            print(f"  {k}: {v}")

    print("\n=== Active App ===")
    app = get_active_app(ip)
    if app:
        print(f"  {app.get('name', 'Unknown')} (id={app.get('id')})")
    else:
        print("  (none or unknown)")

    print("\n=== Media Player ===")
    mp = get_media_player(ip)
    if mp:
        for k, v in sorted(mp.items()):
            print(f"  {k}: {v}")
    else:
        print("  (no active media player state)")

def print_apps(ip: str) -> None:
    apps = get_apps(ip)
    if not apps:
        print("No apps returned (check IP and 'Control by mobile apps' setting).")
        return
    print(f"{'ID':<8} {'Name'}")
    print("-" * 40)
    for a in apps:
        print(f"{a['id']:<8} {a['name']}")

def do_launch(ip: str, app: str) -> None:
    app_lower = app.lower()

    # Try numeric ID first
    if app.isdigit():
        launch_app(ip, app)
        print(f"Launched app ID {app}")
        return

    # Try high-level library
    roku = get_roku(ip)
    if roku:
        try:
            roku[app].launch()
            print(f"Launched '{app}' via library")
            return
        except Exception:
            pass

    # Fallback: try to find ID by name (exact or partial match)
    apps = get_apps(ip)
    for a in apps:
        name_lower = a["name"].lower()
        if name_lower == app_lower or app_lower in name_lower:
            launch_app(ip, a["id"])
            print(f"Launched '{a['name']}' (id={a['id']})")
            return

    # Last resort: try launching the string directly as an ID (for things like "tvinput.hdmi2")
    launch_app(ip, app)
    print(f"Tried launching '{app}' directly as ID (may have worked)")

    # If we get here without error, it might have succeeded or the device ignored it
    print("If nothing happened, use exact name from 'apps' list or the ID.")

def interactive(ip: str) -> None:
    print(f"\nRoku Interactive Playground @ {ip}")
    print("Type keys (Home, Select, Play, VolumeUp, etc.), 'status', 'apps', 'launch <name>',")
    print("a macro name, or 'quit'.\n")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not cmd:
            continue
        if cmd.lower() in ("q", "quit", "exit"):
            print("Bye.")
            break
        if cmd.lower() == "status":
            print_status(ip)
            continue
        if cmd.lower() == "apps":
            print_apps(ip)
            continue
        if cmd.lower().startswith("launch "):
            _, *rest = cmd.split(None, 1)
            if rest:
                do_launch(ip, rest[0])
            continue
        if cmd.lower() in MACROS:
            run_macro(ip, cmd)
            continue

        # Assume it's a key
        print(f"Sending: {cmd}")
        send_key(ip, cmd)

def main():
    parser = argparse.ArgumentParser(
        description="Roku TV control & playground toolkit (ECP over HTTP)"
    )
    parser.add_argument("--ip", required=True, help="Roku device IP address (e.g. 192.168.1.42)")
    sub = parser.add_subparsers(dest="cmd")

    p_press = sub.add_parser("press", help="Send a single keypress")
    p_press.add_argument("key", help="Key name (Home, Select, Play, VolumeUp, PowerOn, etc.)")

    sub.add_parser("status", help="Show device info + active app + media state")
    sub.add_parser("apps", help="List installed apps with IDs")

    p_launch = sub.add_parser("launch", help="Launch an app by name or numeric ID")
    p_launch.add_argument("app", help="App name (e.g. Netflix) or ID")

    p_macro = sub.add_parser("macro", help="Run a predefined macro/scene")
    p_macro.add_argument("name", help=f"One of: {', '.join(MACROS.keys())}")

    sub.add_parser("interactive", help="Interactive shell for playing around")

    # New: fleet / cool stuff command for dashboard mode
    p_fleet = sub.add_parser("fleet", help="Cool stuff: Prepare TV for fleet dashboard (Home + volume + optional cast notes)")
    p_fleet.add_argument("--cast", action="store_true", help="Also remind to start mirroring the web dashboard")

    args = parser.parse_args()

    ip = args.ip.strip()

    if args.cmd == "press":
        send_key(ip, args.key)
        print(f"Sent key: {args.key}")
    elif args.cmd == "status":
        print_status(ip)
    elif args.cmd == "apps":
        print_apps(ip)
    elif args.cmd == "launch":
        do_launch(ip, args.app)
    elif args.cmd == "macro":
        run_macro(ip, args.name)
    elif args.cmd == "fleet":
        print("=== FLEET DASHBOARD MODE ===")
        send_key(ip, "Home")
        time.sleep(0.8)
        # Set a reasonable volume
        for _ in range(3):
            send_key(ip, "VolumeDown")
            time.sleep(0.15)
        print_status(ip)
        if args.cast:
            print("\n[CAST] Now start screen mirroring / AirPlay from your PC or Mac to this Roku.")
            print("       Open the fleet dashboard web page and mirror the tab/window.")
            print("       Run the web server if needed: cd ~/Work/active-projects/fleet-roku-dashboard/fleet-dashboard-web && python3 -m http.server 8080")
        print("\nTV is ready for the extended dashboard. Use other commands to control further.")
    elif args.cmd == "interactive":
        interactive(ip)
    else:
        # No subcommand → show a little help + status
        print("No command given. Here's current status:\n")
        print_status(ip)
        print("\nTry --help for commands, or use 'interactive' mode to explore.")
        print("New cool command: python3 roku_ctl.py --ip 10.0.0.73 fleet --cast")

if __name__ == "__main__":
    main()