import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

def generate_lofi_prompt(image_path):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")

    genai.configure(api_key=api_key)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")

    img = Image.open(image_path)
    prompt = (
        "Describe this image for creating prompt for a music. It should include its emotion, "
        "the people, and the surroundings to generate the prompt in maximum of 200 words without any comments or suggestions."
    )
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, img])
    return response.text
