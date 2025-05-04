from flask import Flask, request, jsonify
import mimetypes
import base64
import os
import google.generativeai as genai  # ✅ this avoids the naming conflict

app = Flask(__name__)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "Show me something awesome")

    client = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
    response = client.generate_content(prompt, stream=True)

    for chunk in response:
        if chunk.parts:
            for part in chunk.parts:
                if hasattr(part, "inline_data"):
                    encoded = base64.b64encode(part.inline_data.data).decode()
                    return jsonify({
                        "mimeType": part.inline_data.mime_type,
                        "data": encoded,
                        "fileExtension": mimetypes.guess_extension(part.inline_data.mime_type)
                    })
    return jsonify({"error": "No image generated"}), 400
