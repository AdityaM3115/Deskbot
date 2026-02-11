import speech_recognition as sr

def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = r.listen(
                source,
                timeout=5,          # Wait max 5 sec for speech
                phrase_time_limit=20 # Max speech length 8 sec
            )
        except sr.WaitTimeoutError:
            return "No speech detected"

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Request error: {e}"