import google.generativeai as genai
import os
import sys
import json
from dotenv import load_dotenv
from PIL import Image

def generate_lofi_prompt(image_path):
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("No API key found. Make sure you have a .env file with GOOGLE_API_KEY set.")

    genai.configure(api_key=api_key)

    
    model = genai.GenerativeModel('gemini-1.5-flash')

    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")

    
    img = Image.open(image_path)
    prompt = "Describe this image for creating prompt for an music it should include its emotion and the people and the surroundings to generate the prompt in maximum of 200 words without any comments or suggesstions"
    response = model.generate_content([prompt, img])
    
    return response.text

# Main execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gemini_lofi.py <image_path> [--json]")
        exit(1)
    
    image_path = sys.argv[1]
    json_output = "--json" in sys.argv
    
    try:
        result = generate_lofi_prompt(image_path)
        
        if json_output:
            print(json.dumps({
                "success": True,
                "image_path": image_path,
                "lofi_prompt": result
            }))
        else:
            print(result)
            
    except Exception as e:
        if json_output:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
        else:
            print(f"❌ Error: {e}")