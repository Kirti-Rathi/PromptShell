import speech_recognition as sr
import time

def listen_and_transcribe():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (press Ctrl+C to stop)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            time.sleep(0.5)
            audio=recognizer.listen(source, timeout=8)
            print("🧠 Transcribing...")
            try:
                query = recognizer.recognize_google(audio)
                print(f"\n🗣️ User said: \"{query}\"\n")
                return query
            except sr.UnknownValueError:
                print("⚠️ Could not understand the audio.")
            except sr.RequestError as e:
                print(f"⚠️ Speech Recognition error: {e}")
    except OSError:
        print("❌ Microphone not found or access denied.")

    return None
