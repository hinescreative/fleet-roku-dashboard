#!/usr/bin/env python3
"""
Fleet Control Panel - Click buttons instead of terminal.
Super simple GUI for your Roku TV (10.0.0.73) + Fleet Dashboard.

Run with: python3 fleet_gui.py
Then just click the big buttons.

This starts the web dashboard server automatically when needed,
preps the TV, and lets you control everything with clicks.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import webbrowser
import os
import time
import socket

# === CONFIG - change if needed ===
ROKU_IP = "10.0.0.73"
CTL_SCRIPT = os.path.expanduser("~/roku-experiments/roku_ctl.py")
DASH_DIR = os.path.expanduser("~/roku-experiments/fleet-dashboard-web")
DASH_PORT = 8080
DASH_URL = f"http://localhost:{DASH_PORT}"

# Colors for TV-friendly look
BG = "#1a1a2e"
FG = "#ffffff"
ACCENT = "#00ff9f"
BUTTON_BG = "#16213e"
BUTTON_FG = "#ffffff"

def run_command(cmd, show_output=True):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        output = (result.stdout + result.stderr).strip()
        if show_output and output:
            print(f"[COMMAND] {cmd}\n{output}")
        return output, result.returncode == 0
    except Exception as e:
        return str(e), False

def is_port_open(port):
    """Check if the dashboard server is already running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_dashboard_server():
    """Start the web dashboard server in background if not running."""
    if is_port_open(DASH_PORT):
        return True, "Dashboard already running"
    
    cmd = f'cd "{DASH_DIR}" && python3 -m http.server {DASH_PORT} > /tmp/fleet_dash.log 2>&1 &'
    output, success = run_command(cmd, show_output=False)
    time.sleep(1.5)  # Give it time to start
    if is_port_open(DASH_PORT):
        return True, "Dashboard server started"
    return False, "Failed to start dashboard server"

def run_fleet_command(extra=""):
    """Run the main fleet prep (Home + volume + ready for cast)."""
    cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} fleet {extra}'
    output, success = run_command(cmd)
    return success, output

def send_tv_command(action):
    """Send simple TV commands via the control script."""
    if action == "home":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} press Home'
    elif action == "plex":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} launch "Plex - Free Movies & TV"'
    elif action == "youtube":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} launch YouTube'
    elif action == "xbox":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} launch "tvinput.hdmi2"'  # or "Xbox"
    elif action == "volume_up":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} press VolumeUp'
    elif action == "volume_down":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} press VolumeDown'
    elif action == "status":
        cmd = f'python3 "{CTL_SCRIPT}" --ip {ROKU_IP} status'
    else:
        return False, "Unknown action"
    
    output, success = run_command(cmd)
    return success, output

class FleetControlPanel:
    def __init__(self, root):
        self.root = root
        root.title("Fleet TV Control")
        root.geometry("520x620")
        root.configure(bg=BG)
        root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 14, "bold"), padding=12)
        style.configure("Accent.TButton", background=ACCENT, foreground=BG)
        
        # Header
        header = tk.Label(root, text="🚀 FLEET DASHBOARD", 
                          font=("Helvetica", 28, "bold"), bg=BG, fg=ACCENT)
        header.pack(pady=(20, 5))
        
        sub = tk.Label(root, text="Roku TV @ 10.0.0.73 • One-Click Mode", 
                       font=("Helvetica", 12), bg=BG, fg="#aaaaaa")
        sub.pack(pady=(0, 15))
        
        # Big main button
        main_frame = tk.Frame(root, bg=BG)
        main_frame.pack(pady=10, padx=20, fill="x")
        
        self.main_btn = tk.Button(main_frame, text="START FLEET DASHBOARD\n(Starts web page + preps TV)", 
                                  command=self.start_fleet,
                                  font=("Helvetica", 16, "bold"), 
                                  bg=ACCENT, fg=BG, height=3, width=35,
                                  relief="flat", activebackground="#00cc7a")
        self.main_btn.pack()
        
        # TV Control buttons
        tv_label = tk.Label(root, text="TV CONTROLS (click to send to Roku)", 
                            font=("Helvetica", 11), bg=BG, fg="#888888")
        tv_label.pack(pady=(15, 5))
        
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(padx=20)
        
        buttons = [
            ("🏠 Home", "home"),
            ("▶️ Launch Plex", "plex"),
            ("📺 Launch YouTube", "youtube"),
            ("🎮 Switch to Xbox (HDMI2)", "xbox"),
            ("🔊 Volume Up", "volume_up"),
            ("🔉 Volume Down", "volume_down"),
            ("📊 Show Status", "status"),
        ]
        
        for i, (text, action) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = tk.Button(btn_frame, text=text, 
                            command=lambda a=action: self.run_action(a),
                            font=("Helvetica", 12), bg=BUTTON_BG, fg=BUTTON_FG,
                            width=18, height=2, relief="flat")
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        # Status box
        status_label = tk.Label(root, text="Last Action:", font=("Helvetica", 10), bg=BG, fg="#888888")
        status_label.pack(pady=(15, 0))
        
        self.status_box = tk.Text(root, height=6, width=50, bg="#0f0f1e", fg=ACCENT,
                                  font=("Courier", 10), relief="flat", wrap="word")
        self.status_box.pack(padx=20, pady=5)
        self.status_box.insert("1.0", "Ready. Click a button above.\n")
        self.status_box.config(state="disabled")
        
        # Footer
        footer = tk.Label(root, text="Open this on your Mac → Click buttons → Mirror to TV\n"
                                     "Dashboard will be at http://localhost:8080", 
                          font=("Helvetica", 9), bg=BG, fg="#666666")
        footer.pack(pady=10)
        
        # Auto-prep on launch (optional, comment out if annoying)
        # self.after(500, lambda: self.log("Tip: Click the big green button to start everything."))
    
    def log(self, msg):
        try:
            if self.status_box.winfo_exists():
                self.status_box.config(state="normal")
                self.status_box.insert("end", f"\n{msg}")
                self.status_box.see("end")
                self.status_box.config(state="disabled")
                self.root.update()
        except:
            pass  # Widget gone or window closed, ignore to prevent crash
    
    def start_fleet(self):
        self.log("Starting Fleet Dashboard...")
        
        # 1. Start web server
        success, msg = self._start_server_thread()
        if success:
            self.log("✓ Web dashboard server started")
        else:
            self.log(f"⚠ {msg}")
        
        # 2. Prep the TV
        self.log("Preparing TV (Home + volume)...")
        success, output = run_fleet_command()
        if success:
            self.log("✓ TV ready for dashboard")
            self.log("→ Now AirPlay / Screen Mirror from this Mac to the Roku")
        else:
            self.log(f"TV prep issue: {output[:100]}...")
        
        # 3. Open browser to dashboard
        try:
            webbrowser.open(DASH_URL)
            self.log(f"Opened {DASH_URL} in browser")
        except:
            self.log("Open http://localhost:8080 manually")
        
        self.log("✅ Done! Mirror the browser tab to your TV now.")
        messagebox.showinfo("Fleet Ready", 
                            "Dashboard is serving.\n\n"
                            "1. Mirror this Mac screen/tab to the Roku (Control Center → Screen Mirroring).\n"
                            "2. The page at http://localhost:8080 should appear on the TV.\n\n"
                            "Use the buttons below for more TV control anytime.")
    
    def _start_server_thread(self):
        def target():
            if not is_port_open(DASH_PORT):
                cmd = f'cd "{DASH_DIR}" && python3 -m http.server {DASH_PORT} > /tmp/fleet_dash.log 2>&1 &'
                run_command(cmd, show_output=False)
                time.sleep(1)
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()
        time.sleep(1.2)
        return is_port_open(DASH_PORT), "Server check complete"
    
    def run_action(self, action):
        self.log(f"Sending: {action}...")
        
        if action == "status":
            success, output = send_tv_command("status")
            self.log("--- TV STATUS ---")
            for line in output.splitlines()[:8]:  # Show first few lines
                self.log(line)
            return
        
        success, output = send_tv_command(action)
        
        if success:
            self.log(f"✓ Sent {action} to TV")
            if action in ["plex", "youtube", "xbox"]:
                self.log("→ TV should have switched apps/inputs")
        else:
            self.log(f"Error: {output}")
        
        # Quick status after action
        time.sleep(0.8)
        _, status = send_tv_command("status")
        active = "Home"
        for line in status.splitlines():
            if "Active App" in line:
                active = line.strip()
                break
        self.log(f"Current: {active}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = FleetControlPanel(root)
    root.mainloop()