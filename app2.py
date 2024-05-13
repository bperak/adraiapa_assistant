from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
import os
import io

# Initialize the OpenAI client
assistant_id = 'asst_pOabkWd3oOjRNzYNZdFoGKu0'
client = OpenAI(api_key="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")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/answer", methods=["GET", "POST"])
def answer():
    data = request.get_json()
    message = data["message"]

    def generate():
        stream = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            stream=True
        )
        for event in stream:
            if event.data.object == "thread.message.delta":
                for content in event.data.delta.content:
                    if content.type == "text":
                        yield content.text.value

    return generate(), {"Content-Type": "text/plain"}

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    audio_data = request.files["audio"].read()
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(io.BytesIO(audio_data))

    with audio as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Unable to recognize speech"})

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    text = request.json["text"]
    tts = gTTS(text=text, lang="en")
    filename = "output.mp3"
    tts.save(filename)
    return jsonify({"url": f"/static/{filename}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8004, debug=False)