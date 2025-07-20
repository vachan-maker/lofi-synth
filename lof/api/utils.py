import sys
import os
import json
import http.client
from PIL import Image
import base64
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUNO_API_KEY = os.getenv("SUNO")

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_lofi_prompt(image_path):
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY")
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API KEY")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")
    
    try:
        img = Image.open(image_path)
        prompt = (
            "Describe this image to create a prompt for lofi/chill/ambient music. "
            "Include the emotion, people, atmosphere, and environment in 200 words max. No suggestions or opinions."
        )
        
        base64_image = image_to_base64(image_path)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, base64_image])
        generated_prompt = response.text.strip()
        
        print(f"Generated prompt: {generated_prompt}")
        
        # Use http.client approach like the Suno documentation
        conn = http.client.HTTPSConnection("api.sunoapi.org")
        
        payload = json.dumps({
            "prompt": generated_prompt,
            "style": "LoFi Chill",
            "title": "Generated Lofi Track",
            "customMode": True,
            "instrumental": True,
            "model": "V3_5",
            "negativeTags": "Heavy Metal, Fast Tempo, EDM",
            "callBackUrl": "https://e213958a8aec.ngrok-free.app/api/callback"
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {SUNO_API_KEY}'
        }
        
        print(f"Sending payload: {payload}")
        
        conn.request("POST", "/api/v1/generate", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        print(f"Response status: {res.status}")
        print(f"Response data: {data.decode('utf-8')}")
        
        if res.status != 200:
            return {
                "success": False,
                "status_code": res.status,
                "response": data.decode('utf-8')
            }
        
        # Parse the JSON response
        response_data = json.loads(data.decode('utf-8'))
        return {
            "success": True,
            "data": response_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python generate_lofi.py <image_path>"
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = generate_lofi_prompt(image_path)
    print(json.dumps(result, indent=2))