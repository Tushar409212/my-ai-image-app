import os
import requests
import io
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Render-এর Environment Variable থেকে শুধুমাত্র ZylaLabs API Key লোড হবে
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY") 

# Zylalabs API Endpoints
TEXT_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20188/generate+image"
IMAGE_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20189/transform+image"

@app.route('/')
def index():
    """ মূল HTML পেজটি দেখানোর জন্য। """
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """ Text to Image ফিচারটি পরিচালনা করে। """
    if not ZYLA_API_KEY:
        return jsonify({"error": "API key is not configured."}), 500
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400
        
        headers = {'Authorization': f'Bearer {ZYLA_API_KEY}'}
        params = {'prompt': prompt, 'width': '512', 'height': '512'}
        
        response = requests.get(TEXT_TO_IMAGE_URL, headers=headers, params=params)
        response.raise_for_status()
        return send_file(io.BytesIO(response.content), mimetype='image/png')
    except Exception as e:
        print(f"Error in generate_image: {e}")
        return jsonify({"error": "An error occurred while generating the image."}), 500

@app.route('/transform-image', methods=['POST'])
def transform_image():
    """ Image to Image ফিচারটি শুধুমাত্র URL ব্যবহার করে পরিচালনা করে। """
    if not ZYLA_API_KEY:
        return jsonify({"error": "API key is not configured."}), 500

    try:
        data = request.get_json()
        prompt = data.get('prompt')
        image_url = data.get('imageUrl')

        if not prompt or not image_url:
            return jsonify({"error": "Prompt and Image URL are required."}), 400

        zylalabs_headers = {'Authorization': f'Bearer {ZYLA_API_KEY}', 'Content-Type': 'application/json'}
        zylalabs_params = {'width': '512', 'height': '512'}
        zylalabs_payload = {'prompt': prompt, 'image': image_url}
        
        zylalabs_response = requests.post(IMAGE_TO_IMAGE_URL, headers=zylalabs_headers, params=zylalabs_params, json=zylalabs_payload)
        zylalabs_response.raise_for_status()

        response_data = zylalabs_response.json()
        final_image_url = response_data.get('url')

        if not final_image_url:
            return jsonify({"error": "API did not return a final image URL."}), 500

        image_response = requests.get(final_image_url)
        image_response.raise_for_status()

        return send_file(io.BytesIO(image_response.content), mimetype='image/png')

    except Exception as e:
        print(f"Error in transform_image: {e}")
        return jsonify({"error": "An internal error occurred during image transformation."}), 500


if __name__ == '__main__':
    app.run(debug=True)
