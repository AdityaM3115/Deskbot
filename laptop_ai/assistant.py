import time
from voice import listen
from gemini_ai import ask_gemini
from speech import speak
from command_handler import classify_command


def clean_response(text):
    return text.replace("\n", " ").strip()


def main():
    print("\n===== DeskBot AI Assistant =====")
    speak("DeskBot is ready.")

    while True:
        user_input = listen()

        # Exit if no speech detected (after timeout)
        if not user_input:
            print("[STATE] No input detected. Exiting.")
            speak("No input detected. Shutting down.")
            break

        print(f"[USER] {user_input}")

        # ---- Command Classification ----
        command_type = classify_command(user_input)
        print(f"[ROUTER] Command type: {command_type}")

        # ---- Routing ----
        if command_type == "exit":
            speak("Shutting down. Goodbye.")
            break

        elif command_type == "ai":
            response = ask_gemini(user_input)

        elif command_type == "app":
            response = "App command detected. Execution will be implemented soon."

        elif command_type == "file":
            response = "File command detected. Execution will be implemented soon."

        elif command_type == "utility":
            response = "Utility command detected. Execution will be implemented soon."

        elif command_type == "system":
            response = "System control command detected. Execution will be implemented soon."

        else:
            response = "Command not recognized."

        print(f"[BOT] {response}")

        response_clean = clean_response(response)
        speak(response_clean)


if __name__ == "__main__":
    main()
