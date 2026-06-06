import tkinter as tk
from tkinter import scrolledtext
import random
import math
import sys
from io import StringIO

# =========================
# GLOBAL STATE
# =========================
bot_state = "idle"
bot_emotion = "neutral"
output_box = None
original_stdout = sys.stdout


class OutputRedirector(StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, message):
        if self.text_widget:
            self.text_widget.config(state="normal")
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.config(state="disabled")
        original_stdout.write(message)
        return len(message)

    def flush(self):
        original_stdout.flush()


def update_gui_state(state, emotion="neutral"):
    global bot_state, bot_emotion
    bot_state = state
    bot_emotion = emotion
    status_label.config(text=f"Status: {state.capitalize()}")


# =========================
# WINDOW
# =========================
root = tk.Tk()
root.title("DeskBot AI")
root.geometry("1000x600")
root.configure(bg="#0f1117")
root.resizable(False, False)

container = tk.Frame(root, bg="#0f1117")
container.place(relx=0.5, rely=0.5, anchor="center")

canvas = tk.Canvas(container, width=450, height=220,
                   bg="#0f1117", highlightthickness=0)
canvas.grid(row=0, column=0, pady=(0, 15))

# =========================
# BASE POSITIONS
# =========================
eye_size = 80
eye_spacing = 30
center_x = 225
base_y = 70
corner = 22

left_base_x = center_x - eye_spacing - eye_size
right_base_x = center_x + eye_spacing

# =========================
# ROUNDED SQUARE
# =========================
def rounded_square(x, y, size, radius, color, tag):
    canvas.create_rectangle(x+radius, y,
                            x+size-radius, y+size,
                            fill=color, outline="", tags=tag)
    canvas.create_rectangle(x, y+radius,
                            x+size, y+size-radius,
                            fill=color, outline="", tags=tag)
    canvas.create_arc(x, y,
                      x+2*radius, y+2*radius,
                      start=90, extent=90,
                      fill=color, outline="", tags=tag)
    canvas.create_arc(x+size-2*radius, y,
                      x+size, y+2*radius,
                      start=0, extent=90,
                      fill=color, outline="", tags=tag)
    canvas.create_arc(x, y+size-2*radius,
                      x+2*radius, y+size,
                      start=180, extent=90,
                      fill=color, outline="", tags=tag)
    canvas.create_arc(x+size-2*radius, y+size-2*radius,
                      x+size, y+size,
                      start=270, extent=90,
                      fill=color, outline="", tags=tag)

# =========================
# EYEBROWS
# =========================
left_brow = canvas.create_line(0, 0, 0, 0, width=3, fill="#00eaff")
right_brow = canvas.create_line(0, 0, 0, 0, width=3, fill="#00eaff")

# =========================
# BLINK
# =========================
left_lid = canvas.create_rectangle(0, 0, 0, 0, fill="#0f1117", outline="")
right_lid = canvas.create_rectangle(0, 0, 0, 0, fill="#0f1117", outline="")
lid_offset = -8


def blink():
    close_eyes(0)


def close_eyes(h):
    if h >= eye_size:
        root.after(120, open_eyes, eye_size)
        return
    canvas.coords(left_lid,
                  left_base_x,
                  base_y + lid_offset,
                  left_base_x+eye_size,
                  base_y + lid_offset + h)
    canvas.coords(right_lid,
                  right_base_x,
                  base_y + lid_offset,
                  right_base_x+eye_size,
                  base_y + lid_offset + h)
    root.after(10, close_eyes, h+10)


def open_eyes(h):
    if h <= 0:
        schedule_next_blink()
        return
    canvas.coords(left_lid,
                  left_base_x,
                  base_y + lid_offset,
                  left_base_x+eye_size,
                  base_y + lid_offset + h)
    canvas.coords(right_lid,
                  right_base_x,
                  base_y + lid_offset,
                  right_base_x+eye_size,
                  base_y + lid_offset + h)
    root.after(10, open_eyes, h-10)


def schedule_next_blink():
    root.after(random.randint(3000, 6000), blink)


schedule_next_blink()

# =========================
# ANIMATION
# =========================
pulse = 0


def clamp(v):
    return max(0, min(255, v))


def draw_eyebrows(offset_y, pulse_value):
    lx = left_base_x
    rx = right_base_x
    base_brow_y = base_y - 12 + offset_y

    if bot_state == "listening":
        base_brow_y -= abs(math.sin(pulse_value * 2)) * 2

    elif bot_state == "thinking":
        base_brow_y -= abs(math.sin(pulse_value)) * 3

    elif bot_state == "speaking":
        base_brow_y -= math.sin(pulse_value * 2) * 1.5

    elif bot_state == "camera":
        base_brow_y -= abs(math.sin(pulse_value)) * 2

    # Neutral default
    left_coords  = (lx+20, base_brow_y, lx+60, base_brow_y)
    right_coords = (rx+20, base_brow_y, rx+60, base_brow_y)

    if bot_emotion == "happy":
        left_coords  = (lx+20, base_brow_y+4, lx+60, base_brow_y)
        right_coords = (rx+20, base_brow_y,   rx+60, base_brow_y+4)

    elif bot_emotion == "focused":
        left_coords  = (lx+20, base_brow_y,   lx+60, base_brow_y+4)
        right_coords = (rx+20, base_brow_y+4, rx+60, base_brow_y)

    elif bot_emotion == "curious":
        left_coords  = (lx+20, base_brow_y-3, lx+60, base_brow_y)
        right_coords = (rx+20, base_brow_y,   rx+60, base_brow_y-3)

    canvas.coords(left_brow,  *left_coords)
    canvas.coords(right_brow, *right_coords)


def animate():
    global pulse
    pulse += 0.08

    idle_offset = 0

    if bot_state == "idle":
        idle_offset = math.sin(pulse) * 1.5

    elif bot_state == "listening":
        idle_offset = math.sin(pulse * 1.5) * 1

    elif bot_state == "thinking":
        idle_offset = abs(math.sin(pulse)) * 3

    elif bot_state == "speaking":
        idle_offset = math.sin(pulse * 2) * 1

    elif bot_state == "camera":
        # Slow, steady pulse — eye is "watching"
        idle_offset = math.sin(pulse * 0.5) * 2

    canvas.delete("left_eye")
    canvas.delete("right_eye")

    brightness = clamp(int(210 + 25 * math.sin(pulse)))

    # Eye color changes per state
    if bot_state == "camera":
        color = f"#00ff{brightness:02x}"   # green tint while camera active
    else:
        color = f"#00{brightness:02x}ff"   # default cyan/blue

    rounded_square(left_base_x,  base_y + idle_offset,
                   eye_size, corner, color, "left_eye")
    rounded_square(right_base_x, base_y + idle_offset,
                   eye_size, corner, color, "right_eye")

    draw_eyebrows(idle_offset, pulse)

    canvas.tag_raise(left_brow)
    canvas.tag_raise(right_brow)
    canvas.tag_raise(left_lid)
    canvas.tag_raise(right_lid)

    root.after(30, animate)


animate()

# =========================
# UI
# =========================
title = tk.Label(container, text="HELLO, I AM NEMO",
                 font=("Segoe UI", 20, "bold"),
                 fg="#e6edf3", bg="#0f1117")
title.grid(row=1, column=0)

status_label = tk.Label(container,
                        text="Status: Idle",
                        font=("Segoe UI", 11, "bold"),
                        fg="#58a6ff",
                        bg="#0f1117")
status_label.grid(row=2, column=0, pady=(5, 10))

output_box = scrolledtext.ScrolledText(
    container,
    width=85,
    height=6,
    font=("Consolas", 11),
    bg="#161b22",
    fg="#c9d1d9"
)
output_box.grid(row=3, column=0, pady=5)
output_box.insert(tk.END, "Bonjour !!.\n")
output_box.configure(state="disabled")

sys.stdout = OutputRedirector(output_box)

if __name__ == "__main__":
    root.mainloop()
