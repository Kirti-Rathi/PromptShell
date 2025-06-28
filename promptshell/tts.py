import pyttsx3

def speak(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
