from voice import listen
from gemini_ai import ask_gemini
from speech import speak


def main():
    print("DeskBot is ready. Say something...")

    speak("DeskBot is ready.")

    while True:
        try:
            # Listen to user
            text = listen()

            if not text:
                continue

            print("You said:", text)

            # Exit condition
            if text.lower() in ["exit", "quit", "stop"]:
                speak("Shutting down. Goodbye.")
                break

            # Get AI response
            response = ask_gemini(text)

            print("Gemini:", response)

            # Clean response for speech (remove newlines)
            response_clean = response.replace("\n", " ")

            # Speak response
            speak(response_clean)

        except Exception as e:
            print("Error occurred:", e)
            speak("Sorry, something went wrong.")


if __name__ == "__main__":
    main()