import time

from voice import listen
from gemini_ai import ask_gemini
from speech import speak
from command_handler import classify_command
from logger import log_info, log_error

from handlers.app_handler import handle_app_command
from handlers.file_handler import handle_file_command
from handlers.utility_handler import handle_utility_command


# ---------------- CONFIG ----------------
WAKE_WORD = "momo"
DEBUG = True
MIN_COMMAND_LENGTH = 2

# System command keywords (NO "open" included as requested)
SYSTEM_KEYWORDS = [
    "create",
    "rename",
    "copy",
    "move",
    "set",
    "remind",
    "start",
    "stop"
]


# ---------------- RESPONSE ----------------
def respond(message):
    if DEBUG:
        print(f"[BOT] {message}")
    speak(message)


# ---------------- MAIN STATE MACHINE ----------------
def main():
    assistant_active = False
    last_command = None
    passive_timer_start = time.time()

    print("\n===== DeskBot AI Assistant =====")
    speak("DeskBot is ready.")
    log_info("DeskBot started.")

    while True:
        try:
            user_input = listen()
        except Exception as e:
            log_error(f"Listen failure: {e}")
            if DEBUG:
                print(f"[ERROR] Listen failure: {e}")
            continue

        current_time = time.time()

        # ---------------- PASSIVE MODE ----------------
        if not assistant_active:

            if current_time - passive_timer_start > 20:
                log_info("No wake word detected. Shutting down.")
                respond("No wake word detected. Shutting down.")
                break

            if user_input:
                lower_input = user_input.lower()

                if DEBUG:
                    print(f"[USER] {user_input}")

                log_info(f"User said: {user_input}")

                if lower_input in ["exit", "quit", "shutdown"]:
                    log_info("User initiated shutdown.")
                    respond("Shutting down. Goodbye.")
                    break

                if WAKE_WORD in lower_input:
                    assistant_active = True
                    log_info("Wake word detected. Switching to ACTIVE mode.")
                    respond("Yes, I am listening.")
                    continue

            continue

        # ---------------- ACTIVE MODE ----------------
        if not user_input:
            assistant_active = False
            passive_timer_start = time.time()
            log_info("Switching to PASSIVE mode.")
            respond("Going back to sleep.")
            continue

        lower_input = user_input.lower()

        if DEBUG:
            print(f"[USER] {user_input}")

        if len(lower_input.strip()) < MIN_COMMAND_LENGTH:
            continue

        if lower_input in ["exit", "quit", "shutdown"]:
            log_info("User initiated shutdown.")
            respond("Shutting down. Goodbye.")
            break

        if "sleep" in lower_input:
            assistant_active = False
            passive_timer_start = time.time()
            log_info("Manual sleep activated.")
            respond("Going to sleep.")
            continue

        if "repeat" in lower_input:
            if last_command:
                user_input = last_command
                lower_input = user_input.lower()
            else:
                respond("No previous command to repeat.")
                continue

        command_type = classify_command(user_input)
        log_info(f"Router classified command as: {command_type}")

        last_command = user_input

        # ---------------- SOLUTION 1 GUARD ----------------
        if command_type == "ai":
            # If it starts with system keyword → block AI fallback
            if any(lower_input.startswith(keyword) for keyword in SYSTEM_KEYWORDS):
                log_info("Blocked AI fallback due to incomplete system command.")

                respond("Incomplete command. Please provide more details.")
                continue

        # ---------------- ROUTING ----------------
        if command_type == "ai":
            log_info("Sending query to Gemini.")
            response = ask_gemini(user_input)

        elif command_type == "app":
            response = handle_app_command(lower_input)

        elif command_type == "file":
            response = handle_file_command(lower_input)

        elif command_type == "utility":
            response = handle_utility_command(lower_input)

        else:
            response = "Command not recognized."

        respond(response)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
