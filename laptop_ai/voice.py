import speech_recognition as sr

DEBUG = True


def listen():
    recognizer = sr.Recognizer()

    # Improve noise handling
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.non_speaking_duration = 0.5

    with sr.Microphone() as source:
        if DEBUG:
            print("[STATE] Calibrating for ambient noise...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        if DEBUG:
            print("[STATE] Listening...")

        try:
            audio = recognizer.listen(
                source,
                timeout=5,             # wait max 5 seconds for speech start
                phrase_time_limit=15   # max speech duration
            )

        except sr.WaitTimeoutError:
            if DEBUG:
                print("[STATE] Timeout - no speech detected.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        if DEBUG:
            print(f"[RECOGNIZED] {text}")
        return text

    except sr.UnknownValueError:
        if DEBUG:
            print("[ERROR] Could not understand audio.")
        return None

    except sr.RequestError as e:
        if DEBUG:
            print(f"[ERROR] Speech service failed: {e}")
        return None
