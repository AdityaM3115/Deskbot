import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)  # optional: control speed
    engine.say(text)
    engine.runAndWait()
    engine.stop()