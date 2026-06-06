import time
import re

from .voice import listen
from .gemini_ai import ask_gemini
from .speech import speak
from .command_handler import classify_command
from .handlers.app_handler import handle_app_command
from .handlers.file_handler import handle_file_command
from .handlers.utility_handler import handle_utility_command
from .gesture_handler import GestureHandler
from .pi_manager import PiManager


WAKE_WORD = "hello"
MIN_COMMAND_LENGTH = 2


# =========================
# CONTEXT MEMORY
# =========================
class AssistantContext:
    def __init__(self):
        self.last_intent = None
        self.last_file = None
        self.last_app = None
        self.pending_action = None
        self.pending_data = None


# =========================
# HELPERS
# =========================
def is_incomplete(text):
    text = text.strip().lower()

    incomplete_patterns = [
        r"^create\s*$",
        r"^rename\s*$",
        r"^copy\s*$",
        r"^move\s*$",
        r"^set\s*$",
        r"^remind\s*$"
    ]

    for pattern in incomplete_patterns:
        if re.match(pattern, text):
            return True

    return False


def extract_filename(text):
    words = text.split()
    if "file" in words:
        index = words.index("file")
        if index + 1 < len(words):
            return words[index + 1]
    return None


def split_commands(text):
    separators = [" and then ", " then ", " and ", " also "]

    for sep in separators:
        if sep in text:
            return text.split(sep)

    return [text]


# =========================
# MAIN
# =========================
def main(update_state_callback=None, gui_output_callback=None):

    assistant_active = False
    passive_timer_start = time.time()
    last_command = None
    context = AssistantContext()

    # ── Gesture / Pi camera setup ──────────────────────────────
    gesture_handler = GestureHandler(
        speech_engine=None,
        gui_callback=update_state_callback
    )
    pi_manager = PiManager(
        speech_engine=None,
        gui_callback=update_state_callback
    )
    # ──────────────────────────────────────────────────────────

    print("DeskBot is ready.")
    speak("DeskBot is ready.")

    if update_state_callback:
        update_state_callback("idle")

    while True:

        try:
            user_input = listen()
        except Exception as e:
            print("Listen error:", e)
            continue

        current_time = time.time()

        # ================= PASSIVE MODE =================
        if not assistant_active:

            if current_time - passive_timer_start > 20:
                if update_state_callback:
                    update_state_callback("idle")
                speak("No wake word detected. Shutting down.")
                break

            if not user_input:
                continue

            lower_input = user_input.lower()

            print("[USER]", user_input)

            if gui_output_callback:
                gui_output_callback(f"[USER] {user_input}")

            if lower_input in ["exit", "quit", "shutdown"]:
                if update_state_callback:
                    update_state_callback("idle")
                speak("Shutting down.")
                break

            if WAKE_WORD in lower_input:
                assistant_active = True
                if update_state_callback:
                    update_state_callback("listening")
                speak("Yes, I am listening.")
                continue

            continue

        # ================= ACTIVE MODE =================

        if not user_input:
            # BUG FIX 3 — don't sleep while camera mode is active
            if gesture_handler.running:
                continue
            assistant_active = False
            passive_timer_start = time.time()
            if update_state_callback:
                update_state_callback("idle")
            speak("Going back to sleep.")
            continue

        lower_input = user_input.lower()

        print("[USER]", user_input)

        if gui_output_callback:
            gui_output_callback(f"[USER] {user_input}")

        if len(lower_input.strip()) < MIN_COMMAND_LENGTH:
            continue

        # EXIT
        if lower_input in ["exit", "quit", "shutdown"]:
            if update_state_callback:
                update_state_callback("idle")
            speak("Shutting down.")
            break

        # SLEEP
        if "sleep" in lower_input:
            # Don't sleep while camera mode is active
            if gesture_handler.running:
                speak("Please stop camera mode first.")
                continue
            assistant_active = False
            passive_timer_start = time.time()
            if update_state_callback:
                update_state_callback("idle")
            speak("Going to sleep.")
            continue

        # REPEAT
        if "repeat" in lower_input:
            if last_command:
                user_input = last_command
                lower_input = user_input.lower()
            else:
                speak("No previous command to repeat.")
                continue

        # Replace "it" with last file
        if "it" in lower_input and context.last_file:
            lower_input = lower_input.replace("it", context.last_file)

        # Incomplete guard
        if is_incomplete(lower_input):
            response = "Please provide more details."
            print("[BOT]", response)
            speak(response)
            continue

        # Confirmation handling
        if context.pending_action:
            if lower_input in ["yes", "confirm"]:
                response = handle_file_command(context.pending_data)
                context.pending_action = None
                context.pending_data = None
                speak(response)
            else:
                speak("Cancelled.")
                context.pending_action = None
                context.pending_data = None
            continue

        # ================= CAMERA / GESTURE MODE =================
        START_TRIGGERS = [
            "switch to camera", "camera mode", "gesture mode",
            "enable camera", "start gesture", "hand control",
        ]
        STOP_TRIGGERS = [
            "stop camera", "close camera", "exit gesture",
            "disable camera", "stop gesture",
        ]

        if any(t in lower_input for t in START_TRIGGERS):
            if gesture_handler.running:
                speak("Gesture mode is already active.")
            else:
                speak("Switching to gesture control mode.")
                # BUG FIX 1 & 2 — start Pi first, wait for full
                # deployment before opening laptop listener.
                # This prevents old Pi processes connecting instantly
                # and sending stale frames.
                pi_manager.start_camera()
                time.sleep(10)
                gesture_handler.start()
            if update_state_callback:
                update_state_callback("idle")
            continue

        if any(t in lower_input for t in STOP_TRIGGERS):
            gesture_handler.stop()
            pi_manager.stop_camera()
            speak("Camera mode closed.")
            if update_state_callback:
                update_state_callback("idle")
            continue

        # ================= THINKING =================
        if update_state_callback:
            update_state_callback("thinking")

        time.sleep(0.4)  # visible thinking state

        # ================= MULTI-STEP COMMANDS =================
        commands = split_commands(lower_input)
        final_response = ""

        for cmd in commands:

            cmd = cmd.strip()
            command_type = classify_command(cmd)
            context.last_intent = command_type
            last_command = cmd

            try:
                if command_type == "file":

                    if "delete" in cmd:
                        context.pending_action = "delete"
                        context.pending_data = cmd
                        speak("Are you sure?")
                        continue

                    response = handle_file_command(cmd)

                    extracted = extract_filename(cmd)
                    if extracted:
                        context.last_file = extracted

                elif command_type == "utility":
                    response = handle_utility_command(cmd)

                elif command_type == "app":
                    response = handle_app_command(cmd)

                else:
                    response = ask_gemini(cmd)

            except Exception as e:
                print("Processing error:", e)
                response = "Something went wrong."

            final_response += response + " "

        final_response = final_response.strip()

        print("[BOT]", final_response)

        if gui_output_callback:
            gui_output_callback(f"[BOT] {final_response}")

        if update_state_callback:
            update_state_callback("speaking")

        speak(final_response)

        if update_state_callback:
            update_state_callback("idle")

        time.sleep(0.2)