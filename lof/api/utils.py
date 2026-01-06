# api/utils.py

import os
import json
import sys
import time
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUNO_API_KEY = os.getenv("SUNO")

# --- Simple utility ---
def image_to_base64(image_path):
    """Convert image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# --- Gemini prompt generation ---
def generate_lofi_prompt(image_path):
    """Generate a lofi music prompt from an image using Google Gemini."""
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY")

    genai.configure(api_key=GOOGLE_API_KEY)

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


def submit_music_generation(prompt_text):
    """Submit music generation request to Suno API."""
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API key")
    
    url = "https://api.sunoapi.org/api/v1/generate"
    payload = {
        "prompt": prompt_text,
        "style": "Classical",
        "title": "Peaceful Piano Meditation",
        "customMode": True,
        "instrumental": True,
        "model": "V3_5",
        "negativeTags": "Heavy Metal, Upbeat Drums"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {SUNO_API_KEY}'
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    task_id = result.get('task_id') or result.get('id')
    
    return {
        "task_id": task_id,
        "initial_response": result
    }


def check_generation_status(task_id):
    """Check the status of a music generation task."""
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API key")
    
    url = f"https://api.sunoapi.org/api/v1/music/status/{task_id}"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {SUNO_API_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        }


def poll_for_completion(task_id, poll_interval=10, max_wait_time=300):
    """Poll for music generation completion with timeout."""
    start_time = time.time()
    
    while (time.time() - start_time) < max_wait_time:
        status_response = check_generation_status(task_id)
        
        if 'error' in status_response:
            return {
                'success': False,
                'error': status_response['error']
            }
        
        music_info = extract_music_info(status_response)
        
        if music_info['status'] == 'complete':
            return {
                'success': True,
                'status': 'complete',
                'audio_urls': music_info['audio_urls'],
                'tracks': music_info['tracks'],
                'metadata': music_info['metadata']
            }
        elif music_info['status'] == 'failed':
            return {
                'success': False,
                'status': 'failed',
                'error': ', '.join(music_info['errors']) if music_info['errors'] else 'Unknown error'
            }
        
        time.sleep(poll_interval)
    
    return {
        'success': False,
        'error': 'Timeout waiting for music generation',
        'status': 'timeout'
    }


def extract_music_info(api_response):
    """Extract music information from API response."""
    status = api_response.get('status', 'unknown')
    
    # Extract audio URLs from various possible response structures
    audio_urls = []
    tracks = []
    errors = []
    
    if isinstance(api_response.get('tracks'), list):
        tracks = api_response['tracks']
        audio_urls = [track.get('audio_url') for track in tracks if track.get('audio_url')]
    elif api_response.get('audio_url'):
        audio_urls = [api_response['audio_url']]
    
    if api_response.get('error'):
        errors.append(api_response['error'])
    
    progress = api_response.get('progress', 0)
    
    return {
        'status': status,
        'progress': progress,
        'audio_urls': audio_urls,
        'tracks': tracks,
        'errors': errors,
        'metadata': {
            'title': api_response.get('title'),
            'style': api_response.get('style'),
            'duration': api_response.get('duration')
        }
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        error_result = {
            "success": False,
            "error": "Usage: python utils.py <image_path>"
        }
        print(json.dumps(error_result))
        sys.exit(1)
    
    image_path = sys.argv[1]
    try:
        prompt = generate_lofi_prompt(image_path)
        result = {
            "success": True,
            "prompt": prompt
        }
        print(json.dumps(result))
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result))
