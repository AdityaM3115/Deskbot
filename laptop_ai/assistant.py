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

from file_control import (
    create_folder,
    create_file,
    rename_file_keep_extension,
    rename_folder,
    copy_file_keep_extension,
    move_file_keep_extension
)


def clean_response(text):
    return text.replace("\n", " ").strip()


def main():
    print("\n===== DeskBot AI Assistant =====")
    speak("DeskBot is ready.")

    while True:
        user_input = listen()

        if not user_input:
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

            if "close" in lower_input:
                response = close_active_window()

            elif "open" in lower_input:
                words = lower_input.split()
                response = None

                for word in words:
                    result = open_website(word)
                    if result:
                        response = result
                        break

                if not response:
                    for word in words:
                        result = open_system_folder(word)
                        if result:
                            response = result
                            break

                if not response:
                    for word in words:
                        result = open_custom_folder(word)
                        if result:
                            response = result
                            break

                if not response:
                    for app in ["chrome", "notepad", "calculator", "explorer"]:
                        if app in lower_input:
                            response = open_application(app)
                            break

                if not response:
                    response = "Application, website, or folder not recognized."

        elif command_type == "file":
            lower_input = user_input.lower()

            # Create folder
            if "create folder" in lower_input:
                folder_name = lower_input.replace("create folder", "").strip()
                response = create_folder(folder_name)

            # Create file (new logic)
            elif "create" in lower_input and "file" in lower_input:
                parts = lower_input.replace("create", "").replace("file", "").strip().split()

                if len(parts) >= 2:
                    file_type = parts[0]
                    file_name = parts[1]
                    response = create_file(file_type, file_name)
                else:
                    response = "Format: create text file filename"

            # Rename file
            elif "rename file" in lower_input:
                try:
                    parts = lower_input.replace("rename file", "").strip().split(" to ")
                    old_name = parts[0].strip()
                    new_name = parts[1].strip()
                    response = rename_file_keep_extension(old_name, new_name)
                except:
                    response = "Format: rename file oldname to newname."

            # Rename folder
            elif "rename folder" in lower_input:
                try:
                    parts = lower_input.replace("rename folder", "").strip().split(" to ")
                    old_name = parts[0].strip()
                    new_name = parts[1].strip()
                    response = rename_folder(old_name, new_name)
                except:
                    response = "Format: rename folder oldname to newname."

            # Copy file
            elif "copy file" in lower_input:
                file_name = lower_input.replace("copy file", "").strip()
                response = copy_file_keep_extension(file_name)

            # Move file
            elif "move file" in lower_input:
                file_name = lower_input.replace("move file", "").strip()
                response = move_file_keep_extension(file_name)

            else:
                response = "File command not recognized."

        else:
            response = "Command not recognized."

        print(f"[BOT] {response}")
        speak(clean_response(response))


if __name__ == "__main__":
    main()
