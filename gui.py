import tkinter as tk
from tkinter import scrolledtext
import random
import math

# =========================
# GLOBAL STATE
# =========================
bot_state = "idle"
bot_emotion = "neutral"

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

# =========================
# MAIN CONTAINER
# =========================
container = tk.Frame(root, bg="#0f1117")
container.place(relx=0.5, rely=0.5, anchor="center")

# =========================
# CANVAS
# =========================
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
# DRAW EYES
# =========================
rounded_square(left_base_x, base_y, eye_size, corner, "#00eaff", "left_eye")
rounded_square(right_base_x, base_y, eye_size, corner, "#00eaff", "right_eye")

# =========================
# EYEBROWS
# =========================
left_brow = canvas.create_line(0,0,0,0, width=3, fill="#00eaff")
right_brow = canvas.create_line(0,0,0,0, width=3, fill="#00eaff")

def draw_eyebrows(offset_y=0):
    lx = left_base_x
    rx = right_base_x
    y = base_y - 10 + offset_y

    if bot_emotion == "happy":
        canvas.coords(left_brow, lx+15, y+5, lx+65, y)
        canvas.coords(right_brow, rx+15, y, rx+65, y+5)

    elif bot_emotion == "focused":
        canvas.coords(left_brow, lx+15, y, lx+65, y+5)
        canvas.coords(right_brow, rx+15, y+5, rx+65, y)

    elif bot_emotion == "curious":
        canvas.coords(left_brow, lx+20, y-2, lx+60, y)
        canvas.coords(right_brow, rx+20, y, rx+60, y)

    else:  # neutral
        canvas.coords(left_brow, lx+20, y, lx+60, y)
        canvas.coords(right_brow, rx+20, y, rx+60, y)

# =========================
# BLINK
# =========================
left_lid = canvas.create_rectangle(0,0,0,0, fill="#0f1117", outline="")
right_lid = canvas.create_rectangle(0,0,0,0, fill="#0f1117", outline="")

def blink():
    close_eyes(0)

def close_eyes(h):
    if h >= eye_size:
        root.after(120, open_eyes, eye_size)
        return
    canvas.coords(left_lid,
                  left_base_x,
                  base_y,
                  left_base_x+eye_size,
                  base_y+h)
    canvas.coords(right_lid,
                  right_base_x,
                  base_y,
                  right_base_x+eye_size,
                  base_y+h)
    root.after(10, close_eyes, h+10)

def open_eyes(h):
    if h <= 0:
        schedule_next_blink()
        return
    canvas.coords(left_lid,
                  left_base_x,
                  base_y,
                  left_base_x+eye_size,
                  base_y+h)
    canvas.coords(right_lid,
                  right_base_x,
                  base_y,
                  right_base_x+eye_size,
                  base_y+h)
    root.after(10, open_eyes, h-10)

def schedule_next_blink():
    root.after(random.randint(3000,6000), blink)

schedule_next_blink()

# =========================
# ANIMATION
# =========================
pulse = 0

def clamp(v):
    return max(0, min(255, v))

def animate():
    global pulse
    pulse += 0.08

    idle_offset = 0
    if bot_state == "idle":
        idle_offset = math.sin(pulse)*1.5

    elif bot_state == "thinking":
        idle_offset = abs(math.sin(pulse))*3

    elif bot_state == "speaking":
        idle_offset = math.sin(pulse*2)*1

    # redraw eyes at base position every frame (NO DRIFT)
    canvas.delete("left_eye")
    canvas.delete("right_eye")

    brightness = clamp(int(210 + 25 * math.sin(pulse)))
    color = f"#00{brightness:02x}ff"

    rounded_square(left_base_x, base_y+idle_offset, eye_size, corner, color, "left_eye")
    rounded_square(right_base_x, base_y+idle_offset, eye_size, corner, color, "right_eye")

    draw_eyebrows(idle_offset)

    root.after(30, animate)

animate()

# =========================
# TITLE
# =========================
title = tk.Label(container, text="HELLO, I AM MOMO",
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

if __name__ == "__main__":
    root.mainloop()
