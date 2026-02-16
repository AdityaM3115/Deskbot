import pyttsx3
import threading

_speech_lock = threading.Lock()

def speak(text):
    with _speech_lock:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
