# import speech_recognition as sr
# import pyttsx3
# import requests
# from docx import Document

# # Initialize TTS engine
# engine = pyttsx3.init()

# def speak(text):
#     engine.say(text)
#     engine.runAndWait()

# def ask_gemini(prompt):
#     api_key = "AIzaSyD5rl09d6lHsf1D7R6-A_M3xht06A2BeDY"
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "contents": [
#             {"parts": [{"text": prompt}]}
#         ]
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     if response.status_code == 200:
#         content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
#         return content
#     else:
#         return "Failed to get a response from Gemini."

# def save_to_doc(text, filename="response.docx"):
#     doc = Document()
#     doc.add_heading('Gemini AI Response', 0)
#     doc.add_paragraph(text)
#     doc.save(filename)

# def listen_and_process():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         speak("Listening for your prompt...")
#         print("Listening...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         prompt = recognizer.recognize_google(audio)
#         print("You said:", prompt)
#         speak("Processing your prompt.")
#         result = ask_gemini(prompt)
#         print("Gemini Response:", result)
#         speak("I have saved the response in a document.")
#         save_to_doc(result)
#     except Exception as e:
#         print(f"Error: {e}")
#         speak("Sorry, I couldn't process that.")

# if __name__ == "__main__":
#     listen_and_process()
