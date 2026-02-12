import time
from voice import listen
from gemini_ai import ask_gemini
from speech import speak
from command_handler import classify_command
from system_control import (
    open_application,
    close_active_window,
    open_website,
    open_system_folder,
    open_custom_folder
)


def clean_response(text):
    return text.replace("\n", " ").strip()


def main():
    print("\n===== DeskBot AI Assistant =====")
    speak("DeskBot is ready.")

    while True:
        user_input = listen()

        if not user_input:
            print("[STATE] No input detected. Exiting.")
            speak("No input detected. Shutting down.")
            break

        print(f"[USER] {user_input}")

        command_type = classify_command(user_input)
        print(f"[ROUTER] Command type: {command_type}")

        if command_type == "exit":
            speak("Shutting down. Goodbye.")
            break

        elif command_type == "ai":
            response = ask_gemini(user_input)

        elif command_type == "app":
            lower_input = user_input.lower()

            # Close
            if "close" in lower_input:
                response = close_active_window()

            elif "open" in lower_input:
                words = lower_input.split()

                # Try website
                for word in words:
                    site_response = open_website(word)
                    if site_response:
                        response = site_response
                        break
                else:
                    # Try system folder
                    for word in words:
                        folder_response = open_system_folder(word)
                        if folder_response:
                            response = folder_response
                            break
                    else:
                        # Try custom folder (AI created on Desktop)
                        for word in words:
                            custom_response = open_custom_folder(word)
                            if custom_response:
                                response = custom_response
                                break
                        else:
                            # Try application
                            for app in ["chrome", "notepad", "calculator", "explorer"]:
                                if app in lower_input:
                                    response = open_application(app)
                                    break
                            else:
                                response = "Application, website, or folder not recognized."
            else:
                response = "Command not recognized."

        elif command_type == "file":
            response = "File command detected. Execution coming soon."

        elif command_type == "utility":
            response = "Utility command detected. Execution coming soon."

        else:
            response = "Command not recognized."

        print(f"[BOT] {response}")
        speak(clean_response(response))


if __name__ == "__main__":
    main()
