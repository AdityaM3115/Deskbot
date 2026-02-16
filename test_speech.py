import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 170)

engine.say("Test one")
engine.runAndWait()

engine.say("Test two")
engine.runAndWait()

engine.say("Test three")
engine.runAndWait()
