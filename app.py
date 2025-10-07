import os
import requests
import io
from flask import Flask, render_template, request, jsonify, send_file
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- Cloudinary কনফিগারেশন শুরু ---
# Render-এর Environment Variable থেকে Cloudinary-এর তথ্য লোড হবে
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
# --- Cloudinary কনফিগারেশন শেষ ---

# Zylalabs API Key
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY")

# Zylalabs API Endpoints
TEXT_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20188/generate+image"
IMAGE_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image-generator+nano+banana+api/20189/transform+image"


@app.route('/')
def index():
    return render_template('index.html')


# Text-to-Image ফাংশনটি অপরিবর্তিত থাকছে
@app.route('/generate-image', methods=['POST'])
def generate_image():
    # ... (এই ফাংশনের কোড আগের মতোই থাকবে, কোনো পরিবর্তন নেই) ...
    if not ZYLA_API_KEY: return jsonify({"error": "API key not configured."}), 500
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt: return jsonify({"error": "Prompt is required."}), 400
        headers = {'Authorization': f'Bearer {ZYLA_API_KEY}'}
        params = {'prompt': prompt, 'width': '512', 'height': '512'}
        response = requests.get(TEXT_TO_IMAGE_URL, headers=headers, params=params)
        if response.status_code == 200:
            return send_file(io.BytesIO(response.content), mimetype='image/png')
        else:
            error_message = response.json().get('error', 'Unknown API error')
            return jsonify({"error": f"API Error: {error_message}"}), response.status_code
    except Exception as e:
        return jsonify({"error": "Internal server error."}), 500


# Image-to-Image ফাংশনটি Cloudinary ব্যবহার করার জন্য পরিবর্তন করা হয়েছে
@app.route('/transform-image', methods=['POST'])
def transform_image():
    if not ZYLA_API_KEY or not os.getenv("CLOUDINARY_CLOUD_NAME"):
        return jsonify({"error": "API keys are not configured correctly."}), 500

    try:
        prompt = request.form.get('prompt')
        if 'imageFile' not in request.files:
            return jsonify({"error": "Image file is required."}), 400
        
        image_file = request.files['imageFile']

        # ধাপ ১: Cloudinary-তে ছবি আপলোড করা
        # SDK ব্যবহার করায় কোড এখন অনেক সহজ এবং নির্ভরযোগ্য
        upload_result = cloudinary.uploader.upload(image_file)
        
        # Cloudinary থেকে পাওয়া নিরাপদ URL
        image_url_from_cloudinary = upload_result['secure_url']

        # ধাপ ২: ZylaLabs API-কে নতুন URL দিয়ে কল করা
        zylalabs_headers = {
            'Authorization': f'Bearer {ZYLA_API_KEY}',
            'Content-Type': 'application/json'
        }
        zylalabs_payload = {
            'prompt': prompt,
            'image': image_url_from_cloudinary
        }
        
        zylalabs_response = requests.post(IMAGE_TO_IMAGE_URL, headers=zylalabs_headers, json=zylalabs_payload)
        zylalabs_response.raise_for_status()

        return send_file(io.BytesIO(zylalabs_response.content), mimetype='image/png')

    except Exception as e:
        print(f"Error in transform_image: {e}")
        return jsonify({"error": "An internal error occurred during image transformation."}), 500


if __name__ == '__main__':
    app.run(debug=True)
