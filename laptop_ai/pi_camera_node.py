# pi_camera_node.py  —  RASPBERRY PI SIDE
# Auto-deployed and started by pi_manager.py via SSH.
# Never run this manually.

import socket, struct, time, cv2, os

LAPTOP_IP    = os.environ.get("NEMO_LAPTOP_IP", "192.168.43.XX")
PORT         = 9999
JPEG_QUALITY = 60
RECONNECT    = 3


def open_camera():
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_video_configuration(
            main={"size": (640, 480), "format": "BGR888"}  # BGR directly — fixes color inversion
        ))
        cam.start()
        time.sleep(0.5)
        print("[PI-CAM] PiCamera2 ready (BGR888)")
        return cam, "picamera2"
    except Exception as e:
        print(f"[PI-CAM] PiCamera2 unavailable ({e}), using VideoCapture")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise RuntimeError("No camera found on this Pi")
    print("[PI-CAM] VideoCapture ready")
    return cap, "opencv"


def read_frame(cam, mode):
    if mode == "picamera2":
        # BGR888 format — no conversion needed, already correct colors
        return cam.capture_array()
    ret, frame = cam.read()
    return frame if ret else None


def stream():
    cam, mode = open_camera()

    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((LAPTOP_IP, PORT))
            print(f"[PI-CAM] Connected to {LAPTOP_IP}:{PORT}")

            frame_count = 0
            t0 = time.time()

            while True:
                frame = read_frame(cam, mode)
                if frame is None:
                    continue

                ret, enc = cv2.imencode(
                    ".jpg", frame,
                    [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
                )
                if not ret:
                    continue

                data = enc.tobytes()
                try:
                    sock.sendall(struct.pack(">I", len(data)) + data)
                except (BrokenPipeError, ConnectionResetError):
                    print("[PI-CAM] Connection lost")
                    break

                frame_count += 1
                if time.time() - t0 >= 5:
                    print(f"[PI-CAM] {frame_count / (time.time() - t0):.1f} FPS")
                    frame_count = 0
                    t0 = time.time()

        except (ConnectionRefusedError, OSError) as e:
            print(f"[PI-CAM] {e}. Retry in {RECONNECT}s")
        finally:
            if sock:
                try: sock.close()
                except Exception: pass

        time.sleep(RECONNECT)


if __name__ == "__main__":
    print(f"[PI-CAM] NEMO Camera Node | Target: {LAPTOP_IP}:{PORT}")
    try:
        stream()
    except KeyboardInterrupt:
        print("[PI-CAM] Stopped.")