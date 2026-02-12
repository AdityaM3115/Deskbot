import speech_recognition as sr

def listen(timeout=5, phrase_time_limit=20):
    recognizer = sr.Recognizer()

    # Increase energy threshold (less sensitive to noise)
    recognizer.energy_threshold = 3000
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("[STATE] Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[ERROR] Speech recognition failed: {e}")
        return None