from flask import Flask, request, jsonify
import mimetypes
import base64
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "A beautiful AI-generated image")

    # Correct model for image generation
    model = genai.GenerativeModel("models/imagegeneration")

    try:
        # Generate image (non-streamed version)
        response = model.generate_content(prompt)

        for part in response.parts:
            if hasattr(part, "inline_data"):
                inline_data = part.inline_data
                encoded_data = base64.b64encode(inline_data.data).decode("utf-8")
                return jsonify({
                    "mimeType": inline_data.mime_type,
                    "data": encoded_data,
                    "fileExtension": mimetypes.guess_extension(inline_data.mime_type)
                })

        return jsonify({"error": "No image content found in response"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bind to Render's assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
