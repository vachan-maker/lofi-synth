import sys
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import requests
import json

def generate_lofi_prompt(image_path):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")

    genai.configure(api_key=api_key)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")

    try:
        img = Image.open(image_path)
        prompt = (
            "Describe this image for creating prompt for a music. It should include its emotion, "
            "the people, and the surroundings to generate the prompt in maximum of 200 words without any comments or suggestions."
        )
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, img])
        
        # Call Suno API
        url = "https://api.sunoapi.org/api/v1/generate"
        payload = json.dumps({
            "prompt": f"{response.text}",
            "style": "Classical",
            "title": "Peaceful Piano Meditation",
            "customMode": True,
            "instrumental": True,
            "model": "V3_5",
            "negativeTags": "Heavy Metal, Upbeat Drums",
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer <your-actual-token>'  # Replace with real token
        }

        suno_response = requests.post(url, headers=headers, data=payload)
        
        # Return structured JSON response
        result = {
            "success": True,
            "prompt": response.text,
            "audioResponse": suno_response.json() if suno_response.headers.get('content-type', '').startswith('application/json') else suno_response.text,
            "audioUrl": None  # Extract from suno_response based on API docs
        }
        
        return json.dumps(result)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        error_result = {
            "success": False,
            "error": "Usage: python generate_lofi.py <image_path>"
        }
        print(json.dumps(error_result))
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = generate_lofi_prompt(image_path)
    print(result)
