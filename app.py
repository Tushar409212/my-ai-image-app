import os
import requests
import io
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Render-এর Environment Variable থেকে API Key লোড হবে
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY") 

# শুধুমাত্র Text-to-Image URL টি রাখা হয়েছে
TEXT_TO_IMAGE_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20188/generate+image"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    if not ZYLA_API_KEY:
        return jsonify({"error": "API key is not configured."}), 500
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        width = data.get('width', '512')
        height = data.get('height', '512')

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400
        
        headers = {'Authorization': f'Bearer {ZYLA_API_KEY}'}
        params = {'prompt': prompt, 'width': width, 'height': height}
        
        response = requests.get(TEXT_TO_IMAGE_URL, headers=headers, params=params)
        response.raise_for_status()
        return send_file(io.BytesIO(response.content), mimetype='image/png')
    except Exception as e:
        print(f"Error in generate_image: {e}")
        error_message = "An error occurred while generating the image."
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json().get('error', e.response.text)
                error_message = f"API Error: {error_details}"
            except:
                error_message = f"API Error: {e.response.text}"
        
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
