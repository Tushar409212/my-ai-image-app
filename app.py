import os
import requests
import io
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# আগের মতোই সব Key লোড হবে
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY") 
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Cloudinary কনফিগারেশন (যদি ব্যবহার করেন)
if CLOUDINARY_CLOUD_NAME:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

# Zylalabs API Endpoints
TEXT_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20188/generate+image"
IMAGE_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20189/transform+image"

@app.route('/')
def index():
    return render_template('index.html')

# Text-to-Image ফাংশনটি অপরিবর্তিত থাকছে
@app.route('/generate-image', methods=['POST'])
def generate_image():
    # ... (এই ফাংশনের কোড আগের মতোই থাকবে, কোনো পরিবর্তন নেই) ...
    # ... (Just keeping the code here for completeness) ...
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

# Image-to-Image ফাংশনটি চূড়ান্তভাবে আপডেট করা হয়েছে
@app.route('/transform-image', methods=['POST'])
def transform_image():
    # ... (Cloudinary আপলোডের অংশটি আগের মতোই থাকবে) ...
    if not ZYLA_API_KEY or not CLOUDINARY_CLOUD_NAME:
        return jsonify({"error": "API keys are not configured correctly."}), 500
    try:
        prompt = request.form.get('prompt')
        if 'imageFile' not in request.files:
            return jsonify({"error": "Image file is required."}), 400
        image_file = request.files['imageFile']
        upload_result = cloudinary.uploader.upload(image_file)
        image_url_from_cloudinary = upload_result['secure_url']

        # --- মূল পরিবর্তন শুরু এখান থেকে ---

        # ১. ZylaLabs API-কে কল করার জন্য সঠিক Headers, Params, এবং Body তৈরি করা
        zylalabs_headers = {
            'Authorization': f'Bearer {ZYLA_API_KEY}',
            'Content-Type': 'application/json'
        }
        # URL-এর সাথে width ও height যোগ করা হচ্ছে
        zylalabs_params = {
            'width': '512',
            'height': '512'
        }
        zylalabs_payload = {
            'prompt': prompt,
            'image': image_url_from_cloudinary
        }
        
        # POST রিকোয়েস্ট পাঠানো হচ্ছে params এবং json উভয়সহ
        zylalabs_response = requests.post(IMAGE_TO_IMAGE_URL, headers=zylalabs_headers, params=zylalabs_params, json=zylalabs_payload)
        zylalabs_response.raise_for_status()

        # ২. ZylaLabs থেকে পাওয়া JSON উত্তর থেকে ছবির URL বের করা
        response_data = zylalabs_response.json()
        final_image_url = response_data.get('url')

        if not final_image_url:
            return jsonify({"error": "API did not return an image URL."}), 500

        # ৩. সেই URL থেকে ছবিটি ডাউনলোড করা
        image_response = requests.get(final_image_url)
        image_response.raise_for_status()

        # ৪. ডাউনলোড করা ছবিটি ব্যবহারকারীকে পাঠানো
        return send_file(io.BytesIO(image_response.content), mimetype='image/png')

    except Exception as e:
        print(f"Error in transform_image: {e}")
        return jsonify({"error": "An internal error occurred during image transformation."}), 500

if __name__ == '__main__':
    app.run(debug=True)
