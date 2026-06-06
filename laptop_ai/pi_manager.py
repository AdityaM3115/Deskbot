import threading
import time
import os
import paramiko
from pathlib import Path

from .speech import speak as _speak

# ── Edit these two lines ─────────────────────────────────────
PI_HOST      = "10.235.145.214"   # your Pi's IP on hotspot
PI_USER      = "pi"
PI_PASSWORD  = "deskbot"  # password you set with passwd
PI_SSH_PORT  = 22

PI_SCRIPTS_DIR   = "/home/pi/nemo"
PI_CAMERA_SCRIPT = f"{PI_SCRIPTS_DIR}/pi_camera_node.py"
LOCAL_CAMERA_SCRIPT = Path(__file__).parent / "pi_camera_node.py"
# ─────────────────────────────────────────────────────────────


class PiManager:

    def __init__(self, speech_engine=None, gui_callback=None):
        self.gui_callback   = gui_callback
        self._ssh           = None
        self._lock          = threading.Lock()
        self._camera_pid    = None
        self.camera_running = False

    # ── Internal helpers ──────────────────────────────────────
    def _say(self, msg):
        _speak(msg)

    def _gui(self, state, text=""):
        if self.gui_callback:
            self.gui_callback(state)

    # ── SSH connection ────────────────────────────────────────
    def _connect(self) -> bool:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                PI_HOST, port=PI_SSH_PORT,
                username=PI_USER, password=PI_PASSWORD,
                timeout=8, banner_timeout=8
            )
            with self._lock:
                self._ssh = client
            print(f"[PI-MGR] SSH connected to {PI_HOST}")
            return True
        except paramiko.AuthenticationException:
            print("[PI-MGR] Wrong password. Check PI_PASSWORD in pi_manager.py")
            return False
        except Exception as e:
            print(f"[PI-MGR] SSH failed: {e}")
            return False

    def _run(self, cmd: str) -> tuple[str, str]:
        with self._lock:
            if self._ssh is None:
                return "", "Not connected"
        try:
            _, stdout, stderr = self._ssh.exec_command(cmd, timeout=15)
            return stdout.read().decode().strip(), stderr.read().decode().strip()
        except Exception as e:
            return "", str(e)

    def _disconnect(self):
        with self._lock:
            if self._ssh:
                try:
                    self._ssh.close()
                except Exception:
                    pass
                self._ssh = None

    # ── Reachability check ────────────────────────────────────
    def is_reachable(self) -> bool:
        return True 

    # ── Deploy pi_camera_node.py to Pi ────────────────────────
    def _deploy_camera_script(self) -> bool:
        with self._lock:
            if self._ssh is None:
                return False
        try:
            sftp = self._ssh.open_sftp()
            self._run(f"mkdir -p {PI_SCRIPTS_DIR}")
            sftp.put(str(LOCAL_CAMERA_SCRIPT), PI_CAMERA_SCRIPT)
            sftp.close()
            print(f"[PI-MGR] Script deployed → {PI_CAMERA_SCRIPT}")
            return True
        except Exception as e:
            print(f"[PI-MGR] Deploy failed: {e}")
            return False

    # ── Start camera node on Pi ───────────────────────────────
    def _start_camera_thread(self):
        print("[DEBUG] Starting camera thread")
        print(f"[DEBUG] PI_HOST = {PI_HOST}")
        if not self.is_reachable():
            print("[DEBUG] is_reachable returned False")
            self._say("Cannot reach the Raspberry Pi. Check the connection.")
            return
        
        print("[DEBUG] Pi is reachable, attempting SSH")
        self._gui("thinking")

        if not self._connect():
            print("[DEBUG] SSH connect failed")
            self._say("Could not connect to the Raspberry Pi.")
            return
        
        print("[DEBUG] SSH connected successfully")

        # Kill any stale process
        self._run("pkill -f pi_camera_node.py 2>/dev/null; sleep 0.3")

        if not self._deploy_camera_script():
            self._say("Could not deploy camera script to Pi.")
            self._disconnect()
            return

        # Get laptop IP to inject into Pi environment
        import socket as _socket
        try:
            laptop_ip = _socket.gethostbyname(_socket.gethostname())
        except Exception:
            laptop_ip = "192.168.43.1"  # fallback hotspot host IP

        launch_cmd = (
            f"NEMO_LAPTOP_IP={laptop_ip} "
            f"nohup python3 {PI_CAMERA_SCRIPT} "
            f"> {PI_SCRIPTS_DIR}/camera.log 2>&1 & echo $!"
        )
        pid_str, err = self._run(launch_cmd)

        if pid_str.isdigit():
            self._camera_pid    = int(pid_str)
            self.camera_running = True
            print(f"[PI-MGR] Camera started on Pi (PID {self._camera_pid})")
            self._gui("camera")
        else:
            print(f"[PI-MGR] Launch failed: {err}")
            self._say("Failed to start camera on Pi.")
            self._gui("idle")

        self._disconnect()

    def start_camera(self):
        if self.camera_running:
            self._say("Pi camera is already active.")
            return
        threading.Thread(target=self._start_camera_thread, daemon=True).start()

    # ── Stop camera node on Pi ────────────────────────────────
    def _stop_camera_thread(self):
        if not self.is_reachable():
            self.camera_running = False
            return
        if not self._connect():
            self.camera_running = False
            return
        if self._camera_pid:
            self._run(f"kill {self._camera_pid} 2>/dev/null || true")
        self._run("pkill -f pi_camera_node.py 2>/dev/null || true")
        self._camera_pid    = None
        self.camera_running = False
        print("[PI-MGR] Camera stopped on Pi.")
        self._disconnect()

    def stop_camera(self):
        threading.Thread(target=self._stop_camera_thread, daemon=True).start()

    # ── Phase 2 stubs (GUI on Pi — future) ───────────────────
    def start_gui_on_pi(self): pass
    def stop_gui_on_pi(self):  pass
