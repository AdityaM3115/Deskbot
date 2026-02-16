import time

from .voice import listen
from .gemini_ai import ask_gemini
from .speech import speak
from .command_handler import classify_command
from .handlers.app_handler import handle_app_command
from .handlers.file_handler import handle_file_command
from .handlers.utility_handler import handle_utility_command


# ---------------- CONFIG ----------------
WAKE_WORD = "momo"
DEBUG = True
MIN_COMMAND_LENGTH = 2


# ---------------- RESPONSE ----------------
def respond(message, update_state_callback):
    if update_state_callback:
        update_state_callback("speaking", "happy")

    if DEBUG:
        print(f"[BOT] {message}")

    speak(message)

    time.sleep(0.2)

    if update_state_callback:
        update_state_callback("idle", "neutral")


# ---------------- MAIN ----------------
def main(update_state_callback=None):

    assistant_active = False
    last_command = None
    passive_timer_start = time.time()

    print("\n===== DeskBot AI Assistant =====")
    speak("DeskBot is ready.")

    while True:

        # ---------------- PASSIVE MODE ----------------
        if not assistant_active:

            if update_state_callback:
                update_state_callback("idle", "neutral")

            if time.time() - passive_timer_start > 20:
                respond("No wake word detected. Shutting down.", update_state_callback)
                break

            if update_state_callback:
                update_state_callback("listening", "curious")

            user_input = listen()

            if user_input:
                lower_input = user_input.lower()

                if DEBUG:
                    print(f"[USER] {user_input}")

                if lower_input in ["exit", "quit", "shutdown"]:
                    respond("Shutting down. Goodbye.", update_state_callback)
                    break

                if WAKE_WORD in lower_input:
                    assistant_active = True
                    respond("Yes, I am listening.", update_state_callback)
                    continue

            continue

        # ---------------- ACTIVE MODE ----------------
        if update_state_callback:
            update_state_callback("listening", "curious")

        user_input = listen()

        if not user_input:
            assistant_active = False
            passive_timer_start = time.time()
            respond("Going back to sleep.", update_state_callback)
            continue

        lower_input = user_input.lower()

        if DEBUG:
            print(f"[USER] {user_input}")

        if len(lower_input.strip()) < MIN_COMMAND_LENGTH:
            continue

        if lower_input in ["exit", "quit", "shutdown"]:
            respond("Shutting down. Goodbye.", update_state_callback)
            break

        if "sleep" in lower_input:
            assistant_active = False
            passive_timer_start = time.time()
            respond("Going to sleep.", update_state_callback)
            continue

        if "repeat" in lower_input:
            if last_command:
                lower_input = last_command.lower()
            else:
                respond("No previous command to repeat.", update_state_callback)
                continue

        if update_state_callback:
            update_state_callback("thinking", "focused")

        command_type = classify_command(lower_input)
        last_command = lower_input

        # ---------------- ROUTING ----------------
        if command_type == "ai":
            response = ask_gemini(lower_input)

        elif command_type == "app":
            response = handle_app_command(lower_input)

        elif command_type == "file":
            response = handle_file_command(lower_input)

        elif command_type == "utility":
            response = handle_utility_command(lower_input)

        else:
            response = "Command not recognized."

        respond(response, update_state_callback)
