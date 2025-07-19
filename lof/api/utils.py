import os
import sys
import time
import json
import requests
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

load_dotenv()   # ← load .env once at import
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUNO_API_KEY   = os.getenv("SUNO")
BASE_URL       = "https://api.sunoapi.org/api"
STYLE          = "Classical"
MODEL          = "V3_5"


if not GOOGLE_API_KEY or not SUNO_API_KEY:
    sys.exit("ERROR: Missing GOOGLE_API_KEY or SUNO in your environment")

genai.configure(api_key=GOOGLE_API_KEY)

def generate_lofi_prompt(image_path: str) -> dict:
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"{image_path} not found")
    
    img = Image.open(image_path)
    prompt_text = (
        "Describe this image for creating a music prompt. "
        "Include its emotion, the people, and the surroundings, "
        "in no more than 200 words, without comments or suggestions."
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    desc_resp = model.generate_content([prompt_text, img])
    music_prompt = desc_resp.text.strip()
    print("🔍 Generated image description prompt:\n", music_prompt)


    payload = {
        "prompt": music_prompt,
        "style": STYLE,
        "title": "Peaceful Piano Meditation",
        "customMode": True,
        "instrumental": True,
        "model": MODEL,
        "negativeTags": "Heavy Metal, Upbeat Drums"
    }
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }
    post_url = f"{BASE_URL}/v1/generate"
    resp = requests.post(post_url, headers=headers, json=payload)
    resp.raise_for_status()

    data = resp.json()
    task_id = data.get("taskId") or data.get("id")
    if not task_id:
        raise RuntimeError(f"No task ID in response: {data}")

    status_url = f"{BASE_URL}/v1/music/status/{task_id}"
    while True:
        time.sleep(5)
        st = requests.get(status_url, headers=headers)
        st.raise_for_status()
        st_data = st.json()
        status = st_data.get("status")
        print(f"⏳ Status: {status}")
        if status == "completed":
            audio_url = st_data["result"]["audio_url"]
            print("✅ Completed! Audio URL:", audio_url)
            return {
                "success": True,
                "prompt": music_prompt,
                "audioUrl": audio_url
            }
        elif status == "failed":
            err = st_data.get("error", "Unknown")
            print("❌ Generation failed:", err)
            return {"success": False, "error": err}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python generate_lofi.py <image_path>"
        }))
        sys.exit(1)

    result = generate_lofi_prompt(sys.argv[1])
    print(json.dumps(result, indent=2))
