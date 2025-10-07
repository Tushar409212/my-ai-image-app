import os
import requests
import io
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Render-এর Environment Variable থেকে API Key লোড হবে
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY") 
# আপনার দেওয়া সর্বশেষ Postman কালেকশন থেকে নেওয়া চূড়ান্ত URL
API_URL = "https://zylalabs.com/api/10640/ai+image+generator+nano+banana+api/20188/generate+image"

@app.route('/')
def index():
    """ মূল HTML পেজটি দেখানোর জন্য। """
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """ ব্যবহারকারীর দেওয়া prompt থেকে ছবি তৈরি করে ফেরত পাঠায়। """
    if not ZYLA_API_KEY:
        return jsonify({"error": "API key is not configured on the server."}), 500

    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        # API-এর জন্য প্রয়োজনীয় Headers এবং Parameters সেট করা হচ্ছে
        headers = {
            'Authorization': f'Bearer {ZYLA_API_KEY}'
        }
        params = {
            'prompt': prompt,
            'width': '512',
            'height': '512'
        }
        
        # GET মেথড ব্যবহার করে API কল করা হচ্ছে
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 200:
            # সফল হলে ছবিটি সরাসরি ফেরত পাঠানো হচ্ছে
            image_data = io.BytesIO(response.content)
            return send_file(image_data, mimetype='image/png')
        else:
            # কোনো সমস্যা হলে error মেসেজ পাঠানো হচ্ছে
            try:
                error_message = response.json().get('error', 'Unknown error from API')
            except ValueError:
                error_message = response.text
            print(f"API Error: {response.status_code} - {error_message}")
            return jsonify({"error": f"API Error: {error_message}"}), response.status_code

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)
