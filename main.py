from flask import Flask, request, jsonify
import google.generativeai as genai
import base64
import os
import mimetypes

app = Flask(__name__)

# ✅ Load Gemini API key from environment
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Use experimental image model
        model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
        response = model.generate_content(prompt, stream=True)

        for chunk in response:
            if chunk.parts:
                for part in chunk.parts:
                    if hasattr(part, "inline_data"):
                        inline_data = part.inline_data
                        encoded_image = base64.b64encode(inline_data.data).decode("utf-8")
                        mime_type = inline_data.mime_type
                        extension = mimetypes.guess_extension(mime_type)

                        return jsonify({
                            "imageBase64": encoded_image,
                            "mimeType": mime_type,
                            "fileExtension": extension
                        })
        return jsonify({"error": "No image generated"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Bind to port Render assigns
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
