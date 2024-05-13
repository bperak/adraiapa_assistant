import os
from flask import Flask, render_template, request, Response, jsonify
from openai import OpenAI
import logging

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize the OpenAI client
assistant_id = os.getenv('ASSISTANT_ID')
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    message = data["message"]

    def generate():
        try:
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
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            yield "An error occurred while generating the response."

    return Response(generate(), content_type="text/plain")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8004, debug=False)
