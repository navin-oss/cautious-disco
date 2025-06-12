import speech_recognition as sr
import pyttsx3
import requests
import json
import re
import os
import subprocess
import webbrowser

# Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site-or-project.com",
    "X-Title": "Jarvis Assistant"
}

# Initialize
engine = pyttsx3.init()
engine.setProperty("rate", 180)

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def callback(recognizer, audio):
    try:
        command = recognizer.recognize_google(audio)
        if command.lower() == "stop":
            engine.stop()
            print("Speech stopped by user")
    except:
        pass

stop_listening = recognizer.listen_in_background(microphone, callback)

def speak(text, allow_interruption=False):
    if allow_interruption:
        stop_listening(wait_for_stop=False)
        stop_listening_new = recognizer.listen_in_background(microphone, callback)
    engine.say(text)
    engine.runAndWait()
    if allow_interruption:
        stop_listening_new(wait_for_stop=False)

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        print("🔍 Recognizing...")
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query
    except:
        return None

def clean_response(text):
    # Remove escape characters
    text = text.encode('utf-8').decode('unicode_escape')  # Converts \n, \t, etc. to real characters
    text = text.replace("\\", "")  # Remove any remaining backslashes

    # Remove markdown and special characters
    text = re.sub(r'[*_#>\[\]{}|]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()

    # Extract only the first sentence for speaking
    sentences = re.split(r'(?<=[.!?]) +', text)
    short_summary = sentences[0] if sentences else text
    return short_summary


def chat_with_deepseek(prompt):
    try:
        data = {
            "model": "deepseek/deepseek-r1-zero:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, an intelligent AI assistant. Speak clearly and briefly. "
                        "Always reply in a short, voice-friendly format. Avoid code, markdown, and long paragraphs."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            raw_answer = result["choices"][0]["message"]["content"]
            print("🧠 AI Raw Response:", raw_answer)
            return clean_response(raw_answer)
        else:
            print("❌ API Error:", response.status_code, response.text)
            return "Sorry, I couldn't get a response from the AI."
    except Exception as e:
        print("❌ Exception:", str(e))
        return "There was a problem connecting to the AI."

# Control Functions
def shutdown():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

def open_chrome():
    speak("Opening Chrome.")
    path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    subprocess.Popen([path])

def search_google(query):
    speak(f"Searching Google for {query}")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def open_folder(folder_name):
    speak(f"Opening folder {folder_name}")
    folder_path = os.path.join("C:\\Users\\YourUsername\\", folder_name)  # ← Change this to your actual Windows username
    if os.path.exists(folder_path):
        os.startfile(folder_path)
    else:
        speak("Sorry, I can't find that folder.")

# Main Loop
if __name__ == "__main__":
    speak("Hello, I am Jarvis. Say 'Jarvis' to activate me.", allow_interruption=False)

    while True:
        print("🕒 Waiting for wake word 'Jarvis'...")
        wake_input = listen()

        if wake_input and "jarvis" in wake_input.lower():
            speak("Yes? What would you like me to do?", allow_interruption=False)
            command = listen()

            if command:
                command_lower = command.lower()

                if any(word in command_lower for word in ["exit", "quit", "stop", "bye"]):
                    speak("Goodbye! Have a great day.", allow_interruption=False)
                    break

                elif "shutdown" in command_lower:
                    shutdown()
                    break

                elif "open chrome" in command_lower:
                    open_chrome()

                elif "search for" in command_lower or "google" in command_lower:
                    search_query = command_lower.replace("search for", "").replace("google", "").strip()
                    if search_query:
                        search_google(search_query)
                    else:
                        speak("What should I search for?")

                elif "open folder" in command_lower:
                    folder = command_lower.replace("open folder", "").strip()
                    open_folder(folder)

                else:
                    response = chat_with_deepseek(command)
                    if response:
                        speak(response, allow_interruption=True)
                    else:
                        speak("I couldn't understand the response.", allow_interruption=False)
            else:
                speak("Sorry, I didn't catch that.", allow_interruption=False)
