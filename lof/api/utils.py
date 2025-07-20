# api/utils.py

import os
import json
import http.client
import time
import threading
from PIL import Image
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUNO_API_KEY = os.getenv("SUNO")

# --- Simple utility ---
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# --- Gemini prompt gen ---
def generate_lofi_prompt(image_path):
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found")
    img = Image.open(image_path)
    prompt = (
        "Describe this image to create a prompt for lofi/chill/ambient music. "
        "Include the emotion, people, atmosphere, and environment in 200 words max. No suggestions or opinions."
    )
    base64_image = image_to_base64(image_path)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, base64_image])
    return response.text.strip()

# --- Suno API helpers ---
def submit_music_generation(generated_prompt, callBackUrl=None):
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API KEY")
    conn = http.client.HTTPSConnection("api.sunoapi.org")
    payload_dict = {
        "prompt": generated_prompt,
        "style": "LoFi Chill",
        "title": "Generated Lofi Track",
        "customMode": True,
        "instrumental": True,
        "model": "V3_5",
        "negativeTags": "Heavy Metal, Fast Tempo, EDM"
    }
    if callBackUrl:
        payload_dict["callBackUrl"] = callBackUrl
    payload = json.dumps(payload_dict)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {SUNO_API_KEY}'
    }
    conn.request("POST", "/api/v1/generate", payload, headers)
    res = conn.getresponse()
    data = res.read()
    if res.status != 200:
        raise Exception(f"API request failed: {res.status} - {data.decode('utf-8')}")
    response_data = json.loads(data.decode('utf-8'))
    task_id = None
    if 'data' in response_data and isinstance(response_data['data'], list):
        if response_data['data'] and 'id' in response_data['data'][0]:
            task_id = response_data['data'][0]['id']
    elif 'id' in response_data:
        task_id = response_data['id']
    if not task_id:
        raise Exception("Could not extract task ID from response")
    return {"task_id": task_id, "initial_response": response_data}

def check_generation_status(task_id):
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API KEY")
    conn = http.client.HTTPSConnection("api.sunoapi.org")
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {SUNO_API_KEY}'
    }
    conn.request("GET", f"/api/v1/generate/{task_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    if res.status == 200:
        return json.loads(data.decode('utf-8'))
    elif res.status == 404:
        return {"error": "Task not found", "status_code": 404}
    elif res.status == 401:
        return {"error": "Unauthorized - check API key", "status_code": 401}
    else:
        return {"error": f"API error: {res.status}", "status_code": res.status}

def extract_music_info(api_response):
    result = {
        'status': 'unknown',
        'progress': 0,
        'audio_urls': [],
        'tracks': [],
        'errors': [],
        'metadata': {}
    }
    if not api_response or 'error' in api_response:
        result['status'] = 'error'
        result['errors'].append(api_response.get('error', 'Unknown error'))
        return result
    tracks_data = []
    if 'data' in api_response:
        if isinstance(api_response['data'], list):
            tracks_data = api_response['data']
        else:
            tracks_data = [api_response['data']]
    elif 'tracks' in api_response:
        tracks_data = api_response['tracks']
    elif 'id' in api_response:
        tracks_data = [api_response]
    if not tracks_data:
        result['status'] = 'no_data'
        return result
    all_complete = True
    any_failed = False
    total_progress = 0
    for track in tracks_data:
        track_info = {
            'id': track.get('id'),
            'status': track.get('status', 'unknown'),
            'title': track.get('title'),
            'audio_url': track.get('audio_url'),
            'video_url': track.get('video_url'),
            'image_url': track.get('image_url'),
            'duration': track.get('duration'),
            'created_at': track.get('created_at'),
            'model_name': track.get('model_name'),
            'prompt': track.get('prompt'),
            'style': track.get('style'),
            'error_message': track.get('error_message')
        }
        track_status = track.get('status', '').lower()
        if track_status in ['complete', 'completed']:
            track_info['progress'] = 100
            if track.get('audio_url'):
                result['audio_urls'].append(track.get('audio_url'))
        elif track_status in ['failed', 'error']:
            any_failed = True
            all_complete = False
            track_info['progress'] = 0
            if track.get('error_message'):
                result['errors'].append(f"Track {track.get('id', 'unknown')}: {track.get('error_message')}")
        elif track_status in ['queued', 'pending']:
            all_complete = False
            track_info['progress'] = 10
        elif track_status in ['processing', 'generating']:
            all_complete = False
            track_info['progress'] = 50
        else:
            all_complete = False
            track_info['progress'] = 0
        total_progress += track_info['progress']
        result['tracks'].append(track_info)
    if any_failed and not result['audio_urls']:
        result['status'] = 'failed'
    elif all_complete and result['audio_urls']:
        result['status'] = 'complete'
    elif any_failed and result['audio_urls']:
        result['status'] = 'partial_complete'
    else:
        result['status'] = 'processing'
    if tracks_data:
        result['progress'] = total_progress / len(tracks_data)
    result['metadata'] = {
        'total_tracks': len(tracks_data),
        'completed_tracks': len([t for t in result['tracks'] if t.get('progress') == 100]),
        'failed_tracks': len([t for t in result['tracks'] if t.get('status') == 'failed']),
        'audio_count': len(result['audio_urls'])
    }
    return result

def poll_for_completion(task_id, poll_interval=10, max_wait_time=300):
    start_time = time.time()
    while (time.time() - start_time) < max_wait_time:
        status_response = check_generation_status(task_id)
        if status_response and 'error' not in status_response:
            music_info = extract_music_info(status_response)
            if music_info['status'] == 'complete':
                return {
                    "success": True,
                    "status": "complete",
                    "data": status_response,
                    "audio_urls": music_info['audio_urls']
                }
            elif music_info['status'] == 'failed':
                return {
                    "success": False,
                    "status": "failed",
                    "error": "Music generation failed",
                    "data": status_response,
                    "errors": music_info['errors']
                }
        time.sleep(poll_interval)
    return {
        "success": False,
        "status": "timeout",
        "error": f"Timeout waiting for completion after {max_wait_time} seconds"
    }


# (Optional) Callback server utilities can be placed here if needed for non-Django workflows

