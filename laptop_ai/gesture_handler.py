import socket, struct, threading, time
import cv2, numpy as np
import webbrowser, subprocess, platform, math, os

from .speech import speak as _speak

CAMERA_STREAM_PORT = 9999
COOLDOWN_SEC       = 2.5


class GestureHandler:

    ACTION_MAP = {
        0: ("Closing camera mode",  "_stop_camera"),
        1: ("Opening YouTube",       "_open_youtube"),
        2: ("Opening Calculator",    "_open_calculator"),
        3: ("Opening File Manager",  "_open_file_manager"),
        4: ("Opening Browser",       "_open_browser"),
        5: ("Taking a screenshot",   "_take_screenshot"),
    }
    GESTURE_NAMES = {
        0: "fist",          1: "one_finger",    2: "two_fingers",
        3: "three_fingers", 4: "four_fingers",  5: "open_palm",
    }

    def __init__(self, speech_engine=None, gui_callback=None):
        self.gui_callback      = gui_callback
        self.running           = False
        self.thread            = None
        self._server_sock      = None
        self.last_action_time  = 0
        self.last_finger_count = -1

    # ── Internal helpers ──────────────────────────────────────
    def _say(self, msg):
        _speak(msg)

    def _gui(self, state):
        if self.gui_callback:
            self.gui_callback(state)

    # ── Vision pipeline ───────────────────────────────────────
    def _skin_mask(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        m = cv2.bitwise_or(
            cv2.inRange(hsv, np.array([0,   20, 70], np.uint8),
                             np.array([25, 255, 255], np.uint8)),
            cv2.inRange(hsv, np.array([170, 20, 70], np.uint8),
                             np.array([180, 255, 255], np.uint8))
        )
        k = np.ones((5, 5), np.uint8)
        m = cv2.dilate(m, k, iterations=2)
        m = cv2.erode(m,  k, iterations=1)
        return cv2.GaussianBlur(m, (5, 5), 0)

    def _hand_contour(self, mask):
        contours, _ = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None
        best = max(contours, key=cv2.contourArea)
        return best if cv2.contourArea(best) > 5000 else None

    def _count_fingers(self, contour):
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is None or len(hull) < 3:
            return 0
        try:
            defects = cv2.convexityDefects(contour, hull)
        except cv2.error:
            return 0
        if defects is None:
            return 0
        count = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            b = math.dist(tuple(contour[f][0]), tuple(contour[s][0]))
            c = math.dist(tuple(contour[f][0]), tuple(contour[e][0]))
            a = math.dist(tuple(contour[s][0]), tuple(contour[e][0]))
            cos_a = (b**2 + c**2 - a**2) / (2 * b * c + 1e-9)
            if math.acos(max(-1.0, min(1.0, cos_a))) <= math.pi / 2 and d > 10000:
                count += 1
        return min(count + 1, 5)

    # ── Action executor ───────────────────────────────────────
    def _execute_action(self, fc):
        now = time.time()
        if fc == self.last_finger_count:
            return
        if now - self.last_action_time < COOLDOWN_SEC:
            return
        if fc not in self.ACTION_MAP:
            return
        self.last_action_time  = now
        self.last_finger_count = fc
        msg, method = self.ACTION_MAP[fc]
        print(f"[GESTURE] {fc} fingers → {msg}")
        threading.Thread(target=self._say, args=(msg,), daemon=True).start()
        self._gui("speaking")
        threading.Thread(target=getattr(self, method), daemon=True).start()

    # ── HUD overlay ───────────────────────────────────────────
    def _draw_hud(self, frame, contour, fc, gname, fps):
        h, w = frame.shape[:2]
        if contour is not None:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.drawContours(frame, [cv2.convexHull(contour)], -1, (0, 100, 255), 2)
        cv2.rectangle(frame, (0, 0), (310, 110), (15, 15, 15), -1)
        cv2.putText(frame, "NEMO GESTURE", (8, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        cv2.putText(frame, f"Fingers: {fc}", (8, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 120), 2)
        cv2.putText(frame, f"Gesture: {gname}", (8, 88),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(frame, f"{fps:.1f}fps", (258, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)
        legend = ["0 Fist→EXIT", "1 Index→YouTube", "2 Peace→Calc",
                  "3 Three→Files", "4 Four→Browser", "5 Palm→Screenshot"]
        px = w - 200
        cv2.rectangle(frame, (px - 4, 0), (w, len(legend) * 22 + 10), (15, 15, 15), -1)
        for i, txt in enumerate(legend):
            cv2.putText(frame, txt, (px, 20 + i * 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                        (0, 255, 100) if i == fc else (130, 130, 130), 1)
        cv2.rectangle(frame, (0, h - 26), (w, h), (15, 15, 15), -1)
        cv2.putText(frame, "Pi stream  |  Q/ESC = quit",
                    (8, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (140, 140, 140), 1)
        return frame

    # ── Socket helpers ────────────────────────────────────────
    def _recv_exact(self, sock, n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Pi disconnected")
            buf += chunk
        return buf

    # ── Main receive loop ─────────────────────────────────────
    def _receive_loop(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", CAMERA_STREAM_PORT))
        srv.listen(1)
        srv.settimeout(1.0)
        self._server_sock = srv
        print(f"[GESTURE] Listening on :{CAMERA_STREAM_PORT}")
        self._gui("camera")

        # Wait for Pi to connect
        client = None
        while self.running:
            try:
                client, addr = srv.accept()
                print(f"[GESTURE] Pi connected from {addr[0]}")
                break
            except socket.timeout:
                continue

        if client is None or not self.running:
            srv.close()
            self._gui("idle")
            return

        threading.Thread(
            target=self._say,
            args=("Pi camera connected. Show your hand.",),
            daemon=True
        ).start()
        self._gui("camera")

        fps_count = 0
        fps_time  = time.time()
        cur_fps   = 0.0

        try:
            while self.running:
                try:
                    raw_len = self._recv_exact(client, 4)
                except ConnectionError as e:
                    print(f"[GESTURE] {e}")
                    break

                frame_len = struct.unpack(">I", raw_len)[0]
                if frame_len > 5_000_000:
                    continue

                try:
                    jpeg_bytes = self._recv_exact(client, frame_len)
                except ConnectionError as e:
                    print(f"[GESTURE] {e}")
                    break

                frame = cv2.imdecode(
                    np.frombuffer(jpeg_bytes, np.uint8),
                    cv2.IMREAD_COLOR
                )
                if frame is None:
                    continue
                frame = cv2.flip(frame, 1)

                mask    = self._skin_mask(frame)
                contour = self._hand_contour(mask)
                fc, gname = 0, "no_hand"

                if contour is not None:
                    fc    = self._count_fingers(contour)
                    gname = self.GESTURE_NAMES.get(fc, "unknown")
                    self._execute_action(fc)

                fps_count += 1
                if time.time() - fps_time >= 1.0:
                    cur_fps   = fps_count / (time.time() - fps_time)
                    fps_count = 0
                    fps_time  = time.time()

                cv2.imshow(
                    "NEMO Gesture [Pi Cam]",
                    self._draw_hud(frame.copy(), contour, fc, gname, cur_fps)
                )
                if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                    break

        finally:
            client.close()
            srv.close()
            cv2.destroyAllWindows()
            self.running           = False
            self.last_finger_count = -1
            print("[GESTURE] Camera mode closed.")
            self._gui("idle")

    # ── App actions ───────────────────────────────────────────
    def _open_youtube(self):
        webbrowser.open("https://www.youtube.com")

    def _open_browser(self):
        webbrowser.open("https://www.google.com")

    def _stop_camera(self):
        self.stop()

    def _open_calculator(self):
        s = platform.system()
        if s == "Linux":
            for a in ["gnome-calculator", "galculator", "xcalc"]:
                try: subprocess.Popen([a]); return
                except FileNotFoundError: pass
        elif s == "Windows":
            subprocess.Popen("calc.exe", shell=True)
        elif s == "Darwin":
            subprocess.Popen(["open", "-a", "Calculator"])

    def _open_file_manager(self):
        s = platform.system()
        if s == "Linux":
            for a in ["nautilus", "thunar", "pcmanfm"]:
                try: subprocess.Popen([a]); return
                except FileNotFoundError: pass
        elif s == "Windows":
            subprocess.Popen("explorer.exe", shell=True)
        elif s == "Darwin":
            subprocess.Popen(["open", os.path.expanduser("~")])

    def _take_screenshot(self):
        ts   = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.expanduser(f"~/Desktop/nemo_{ts}.png")
        s    = platform.system()
        if s == "Linux":
            for cmd in [["scrot", path], ["gnome-screenshot", "-f", path]]:
                try: subprocess.Popen(cmd); return
                except FileNotFoundError: pass
        elif s == "Windows":
            ps = (
                f'Add-Type -AssemblyName System.Windows.Forms;'
                f'$b=New-Object System.Drawing.Bitmap('
                f'[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,'
                f'[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);'
                f'$g=[System.Drawing.Graphics]::FromImage($b);'
                f'$g.CopyFromScreen(0,0,0,0,$b.Size);$b.Save("{path}")'
            )
            subprocess.Popen(["powershell", "-Command", ps])

    # ── Public API ────────────────────────────────────────────
    def start(self):
        if self.running:
            return
        self.running           = True
        self.last_finger_count = -1
        self.thread = threading.Thread(
            target=self._receive_loop, daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False
        try:
            if self._server_sock:
                self._server_sock.close()
        except Exception:
            pass
