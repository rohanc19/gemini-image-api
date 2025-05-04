from flask import Flask, request, jsonify
import mimetypes
import base64
import os
from google import genai
from google.genai import types

app = Flask(__name__)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "Show me something awesome")

    client = genai.Client()
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    ]
    config = types.GenerateContentConfig(response_modalities=["image", "text"])

    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=config
    ):
        if chunk.candidates:
            for candidate in chunk.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        encoded = base64.b64encode(part.inline_data.data).decode()
                        return jsonify({
                            "mimeType": part.inline_data.mime_type,
                            "data": encoded,
                            "fileExtension": mimetypes.guess_extension(part.inline_data.mime_type)
                        })
    return jsonify({"error": "No image generated"}), 400
