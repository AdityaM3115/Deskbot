import tkinter as tk
from tkinter import scrolledtext
from laptop_ai.speech import speak
import random
import math

bot_state = "idle"
bot_emotion = "neutral"
# =========================
# GLOBAL STATE
# =========================
def update_gui_state(state,emotion="neutral"):
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
# CANVAS (EYES)
# =========================
canvas = tk.Canvas(container, width=450, height=220,
                   bg="#0f1117", highlightthickness=0)
canvas.grid(row=0, column=0, pady=(0, 15))

# =========================
# EYE SETTINGS
# =========================
eye_size = 80
eye_spacing = 25
center_x = 225
base_y = 63
corner = 22

left_x = center_x - eye_spacing - eye_size
right_x = center_x + eye_spacing

# =========================
# ROUNDED SQUARE FUNCTION
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
rounded_square(left_x, base_y, eye_size, corner, "#00eaff", "left_eye")
rounded_square(right_x, base_y, eye_size, corner, "#00eaff", "right_eye")

# =========================
# GLOW (Listening)
# =========================
glow_left = canvas.create_rectangle(
    left_x-1, base_y-1,
    left_x+2, base_y+2,
    fill="#00eaff", outline="", state="hidden"
)

glow_right = canvas.create_rectangle(
    right_x-1, base_y-1,
    right_x+2, base_y+2,
    fill="#00eaff", outline="", state="hidden"
)

# =========================
# EYELIDS (Blink)
# =========================
left_lid = canvas.create_rectangle(
    left_x, base_y,
    left_x+eye_size, base_y,
    fill="#0f1117", outline=""
)

right_lid = canvas.create_rectangle(
    right_x, base_y,
    right_x+eye_size, base_y,
    fill="#0f1117", outline=""
)

# =========================
# BLINK SYSTEM
# =========================
def blink():
    close_eyes(0)

def close_eyes(h):
    if h >= eye_size:
        root.after(120, open_eyes, eye_size)
        return
    canvas.coords(left_lid, left_x, base_y,
                  left_x+eye_size, base_y+h)
    canvas.coords(right_lid, right_x, base_y,
                  right_x+eye_size, base_y+h)
    root.after(12, close_eyes, h+8)

def open_eyes(h):
    if h <= 0:
        canvas.coords(left_lid, left_x, base_y,
                      left_x+eye_size, base_y)
        canvas.coords(right_lid, right_x, base_y,
                      right_x+eye_size, base_y)
        schedule_next_blink()
        return
    canvas.coords(left_lid, left_x, base_y,
                  left_x+eye_size, base_y+h)
    canvas.coords(right_lid, right_x, base_y,
                  right_x+eye_size, base_y+h)
    root.after(12, open_eyes, h-8)

def schedule_next_blink():
    root.after(random.randint(3000, 6000), blink)

schedule_next_blink()

# =========================
# EMOTION SYSTEM
# =========================
def apply_emotion():
    # Reset transforms
    canvas.scale("left_eye", 0, 0, 1, 1)
    canvas.scale("right_eye", 0, 0, 1, 1)

    if bot_emotion == "happy":
        canvas.move("left_eye", 0, -1)
        canvas.move("right_eye", 0, -1)

    elif bot_emotion == "curious":
        canvas.move("left_eye", -1, 0)
        canvas.move("right_eye", 1, 0)

    elif bot_emotion == "focused":
        canvas.scale("left_eye", left_x + eye_size/2, base_y + eye_size/2, 1, 0.95)
        canvas.scale("right_eye", right_x + eye_size/2, base_y + eye_size/2, 1, 0.95)

    elif bot_emotion == "neutral":
        pass

# =========================
# ANIMATION ENGINE
# =========================
pulse = 0
thinking_offset = 0

def animate():
    global pulse
    pulse += 0.07

    # Reset glow
    canvas.itemconfig(glow_left, state="hidden")
    canvas.itemconfig(glow_right, state="hidden")

    # IDLE
    if bot_state == "idle":
        brightness = int(210 + 30 * math.sin(pulse))
        color = f"#00{brightness:02x}ff"
        canvas.itemconfig("left_eye", fill=color)
        canvas.itemconfig("right_eye", fill=color)
        apply_emotion()

    # LISTENING
    elif bot_state == "listening":
       glow_intensity = int(170 + 60 * abs(math.sin(pulse)))
       glow_color = f"#00{glow_intensity:02x}ff"

    # Show glow behind eyes
       canvas.itemconfig(glow_left, fill=glow_color, state="normal")
       canvas.itemconfig(glow_right, fill=glow_color, state="normal")

    # Slight brightness shift (no shape change)
       brightness = int(220 + 20 * math.sin(pulse))
       color = f"#00{brightness:02x}ff"

       canvas.itemconfig("left_eye", fill=color)
       canvas.itemconfig("right_eye", fill=color)
       apply_emotion()
       

    # THINKING
    elif bot_state == "thinking":
        global thinking_offset
        offset = 3 * abs(math.sin(pulse))
        delta = offset - thinking_offset
        
        # Move eyes and lids down and up
        canvas.move("left_eye", 0, delta)
        canvas.move("right_eye", 0, delta)
        canvas.move(left_lid, 0, delta)
        canvas.move(right_lid, 0, delta)
        canvas.move(glow_left, 0, delta)
        canvas.move(glow_right, 0, delta)
        
        thinking_offset = offset
        apply_emotion()

    # SPEAKING
    elif bot_state == "speaking":
        brightness = int(200 + 50 * abs(math.sin(pulse*2)))
        color = f"#00{brightness:02x}ff"
        canvas.itemconfig("left_eye", fill=color)
        canvas.itemconfig("right_eye", fill=color)
        apply_emotion()

    root.after(30, animate)

animate()


# =========================
# TITLE
# =========================
title = tk.Label(container, text="DeskBot AI Assistant",
                 font=("Segoe UI", 20, "bold"),
                 fg="#e6edf3", bg="#0f1117")
title.grid(row=1, column=0)

# =========================
# STATUS LABEL
# =========================
status_label = tk.Label(container,
                        text="Status: Idle",
                        font=("Segoe UI", 11, "bold"),
                        fg="#58a6ff",
                        bg="#0f1117")
status_label.grid(row=2, column=0, pady=(5, 10))

# =========================
# OUTPUT BOX
# =========================
output_box = scrolledtext.ScrolledText(
    container,
    width=85,
    height=6,
    font=("Consolas", 11),
    bg="#161b22",
    fg="#c9d1d9"
)
output_box.grid(row=3, column=0, pady=5)
output_box.insert(tk.END, "GUI + Premium Eyes Loaded.\n")
output_box.configure(state="disabled")

# =========================
# TEST STATE BUTTONS
# =========================
def set_state(state,emotion = "neutral"):
    global bot_state,bot_emotion
    bot_state = state
    bot_emotion = emotion
    status_label.config(text=f"Status: {state.capitalize()}")

btn_frame = tk.Frame(container, bg="#0f1117")
btn_frame.grid(row=4, column=0, pady=10)

tk.Button(btn_frame, text="Idle", width=12,
          command=lambda: set_state("idle")).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Listening", width=12,
          command=lambda: set_state("listening")).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Thinking", width=12,
          command=lambda: set_state("thinking")).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Speaking", width=12,
          command=lambda: set_state("speaking")).grid(row=0, column=3, padx=5)


