# api/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
import http.client
import time
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

def check_generation_status(task_id):
    """
    Poll the Suno API to check the status of music generation
    Returns the raw API response or None if failed
    """
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API KEY")
    
    try:
        conn = http.client.HTTPSConnection("api.sunoapi.org")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {SUNO_API_KEY}'
        }
        
        conn.request("GET", f"/api/v1/generate/{task_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        print(f"Status check response code: {res.status}")
        print(f"Status check response data: {data.decode('utf-8')}")
        
        if res.status == 200:
            return json.loads(data.decode('utf-8'))
        elif res.status == 404:
            return {"error": "Task not found", "status_code": 404}
        elif res.status == 401:
            return {"error": "Unauthorized - check API key", "status_code": 401}
        else:
            return {"error": f"API error: {res.status}", "status_code": res.status}
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {"error": "Invalid JSON response from API"}
    except Exception as e:
        print(f"Error checking status: {e}")
        return {"error": f"Connection error: {str(e)}"}

def extract_music_info(api_response):
    """
    Extract useful information from the Suno API response
    Returns a structured dict with status, audio URLs, and metadata
    """
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
    
    # Handle different response structures
    tracks_data = []
    
    if 'data' in api_response:
        if isinstance(api_response['data'], list):
            tracks_data = api_response['data']
        else:
            tracks_data = [api_response['data']]
    elif 'tracks' in api_response:
        tracks_data = api_response['tracks']
    elif 'id' in api_response:
        # Single track response
        tracks_data = [api_response]
    
    if not tracks_data:
        result['status'] = 'no_data'
        return result
    
    # Process each track
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
        
        # Determine track status
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
    
    # Determine overall status
    if any_failed and not result['audio_urls']:
        result['status'] = 'failed'
    elif all_complete and result['audio_urls']:
        result['status'] = 'complete'
    elif any_failed and result['audio_urls']:
        result['status'] = 'partial_complete'
    else:
        result['status'] = 'processing'
    
    # Calculate average progress
    if tracks_data:
        result['progress'] = total_progress / len(tracks_data)
    
    # Add metadata
    result['metadata'] = {
        'total_tracks': len(tracks_data),
        'completed_tracks': len([t for t in result['tracks'] if t.get('progress') == 100]),
        'failed_tracks': len([t for t in result['tracks'] if t.get('status') == 'failed']),
        'audio_count': len(result['audio_urls'])
    }
    
    return result

def generate_lofi_prompt(image_path):
    """Generate LoFi music prompt from image using Google Gemini"""
    
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY")
    
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
        
        return generated_prompt
        
    except Exception as e:
        raise Exception(f"Error generating prompt: {str(e)}")

def submit_music_generation(generated_prompt):
    """Submit music generation request to Suno API"""
    
    if not SUNO_API_KEY:
        raise ValueError("Missing SUNO API KEY")
    
    try:
        conn = http.client.HTTPSConnection("api.sunoapi.org")
        payload = json.dumps({
            "prompt": generated_prompt,
            "style": "LoFi Chill",
            "title": "Generated Lofi Track",
            "customMode": True,
            "instrumental": True,
            "model": "V3_5",
            "negativeTags": "Heavy Metal, Fast Tempo, EDM"
        })
        
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
        
        # Extract task ID from response
        task_id = None
        if 'data' in response_data and isinstance(response_data['data'], list):
            if len(response_data['data']) > 0 and 'id' in response_data['data'][0]:
                task_id = response_data['data'][0]['id']
        elif 'id' in response_data:
            task_id = response_data['id']
        
        if not task_id:
            raise Exception("Could not extract task ID from response")
        
        return {
            "task_id": task_id,
            "initial_response": response_data
        }
        
    except Exception as e:
        raise Exception(f"Music generation submission failed: {str(e)}")

def poll_for_completion(task_id, poll_interval=10, max_wait_time=300):
    """Poll for music generation completion"""
    
    start_time = time.time()
    
    while (time.time() - start_time) < max_wait_time:
        status_response = check_generation_status(task_id)
        
        if status_response and 'error' not in status_response:
            # Use the enhanced extraction logic
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
    
    # Timeout reached
    return {
        "success": False,
        "status": "timeout",
        "error": f"Timeout waiting for completion after {max_wait_time} seconds"
    }

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        
        file = request.FILES.get('file')
        print(f"Received file: {file.name}")
        
        # Save uploaded file
        filename = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        file_path = os.path.join(default_storage.location, filename)
        
        try:
            # Step 1: Generate LoFi prompt from image
            print("Generating LoFi prompt from image...")
            generated_prompt = generate_lofi_prompt(file_path)
            print(f"Generated prompt: {generated_prompt}")
            
            # Step 2: Submit music generation request
            print("Submitting music generation request...")
            generation_result = submit_music_generation(generated_prompt)
            task_id = generation_result["task_id"]
            
            print(f"Task ID: {task_id}")
            
            # Return immediate response with task ID
            return JsonResponse({
                'success': True, 
                'message': 'Music generation started',
                'task_id': task_id,
                'generated_prompt': generated_prompt,
                'initial_response': generation_result["initial_response"]
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Cleaned up file: {file_path}")
            except:
                pass
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

@csrf_exempt
def check_music_status(request, task_id):
    """
    Enhanced endpoint to check the status of music generation by task ID
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'error': 'Only GET method allowed'
        }, status=405)
    
    if not task_id or not task_id.strip():
        return JsonResponse({
            'success': False,
            'error': 'Task ID is required'
        }, status=400)
    
    try:
        print(f"Checking status for task ID: {task_id}")
        
        # Get raw API response
        api_response = check_generation_status(task_id)
        
        if not api_response:
            return JsonResponse({
                'success': False,
                'error': 'Could not fetch status from Suno API',
                'task_id': task_id
            }, status=500)
        
        # If there's an API error, return it
        if 'error' in api_response:
            status_code = api_response.get('status_code', 500)
            return JsonResponse({
                'success': False,
                'error': api_response['error'],
                'task_id': task_id
            }, status=status_code)
        
        # Extract structured information
        music_info = extract_music_info(api_response)
        
        # Build response
        response_data = {
            'success': True,
            'task_id': task_id,
            'status': music_info['status'],
            'progress': music_info['progress'],
            'is_complete': music_info['status'] == 'complete',
            'is_failed': music_info['status'] == 'failed',
            'is_processing': music_info['status'] in ['processing', 'queued', 'pending'],
            'audio_urls': music_info['audio_urls'],
            'tracks': music_info['tracks'],
            'metadata': music_info['metadata'],
            'timestamp': api_response.get('timestamp'),
            'raw_response': api_response  # Include for debugging
        }
        
        # Add errors if any
        if music_info['errors']:
            response_data['errors'] = music_info['errors']
        
        return JsonResponse(response_data)
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'task_id': task_id
        }, status=400)
    
    except Exception as e:
        print(f"Unexpected error checking music status: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'task_id': task_id
        }, status=500)

@csrf_exempt
def generate_and_wait(request):
    """Generate music and wait for completion (blocking endpoint)"""
    
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        
        file = request.FILES.get('file')
        print(f"Received file: {file.name}")
        
        # Save uploaded file
        filename = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        file_path = os.path.join(default_storage.location, filename)
        
        try:
            # Step 1: Generate LoFi prompt from image
            print("Generating LoFi prompt from image...")
            generated_prompt = generate_lofi_prompt(file_path)
            print(f"Generated prompt: {generated_prompt}")
            
            # Step 2: Submit music generation request
            print("Submitting music generation request...")
            generation_result = submit_music_generation(generated_prompt)
            task_id = generation_result["task_id"]
            
            print(f"Task ID: {task_id}")
            print("Polling for completion...")
            
            # Step 3: Poll for completion (this will block)
            completion_result = poll_for_completion(task_id, poll_interval=10, max_wait_time=300)
            
            # Extract audio URLs from completion result
            audio_urls = completion_result.get('audio_urls', [])
            
            return JsonResponse({
                'success': completion_result['success'],
                'task_id': task_id,
                'generated_prompt': generated_prompt,
                'initial_response': generation_result["initial_response"],
                'final_result': completion_result,
                'status': completion_result.get('status'),
                'audio_urls': audio_urls
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Cleaned up file: {file_path}")
            except:
                pass
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

@csrf_exempt 
def check_multiple_tasks(request):
    """
    Check status of multiple tasks at once
    Expects POST request with JSON body: {"task_ids": ["id1", "id2", "id3"]}
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST method allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        
        if not task_ids or not isinstance(task_ids, list):
            return JsonResponse({
                'success': False,
                'error': 'task_ids array is required'
            }, status=400)
        
        results = {}
        
        for task_id in task_ids:
            try:
                api_response = check_generation_status(task_id)
                if api_response and 'error' not in api_response:
                    music_info = extract_music_info(api_response)
                    results[task_id] = {
                        'success': True,
                        'status': music_info['status'],
                        'progress': music_info['progress'],
                        'audio_urls': music_info['audio_urls'],
                        'errors': music_info['errors']
                    }
                else:
                    results[task_id] = {
                        'success': False,
                        'error': api_response.get('error', 'Could not fetch status')
                    }
            except Exception as e:
                results[task_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        return JsonResponse({
            'success': True,
            'results': results,
            'total_tasks': len(task_ids),
            'successful_checks': len([r for r in results.values() if r.get('success')])
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)