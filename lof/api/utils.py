# api/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
import http.client
import time
import threading
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
    """Poll the Suno API to check the status of music generation"""
    try:
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
        else:
            return None
            
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

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
            # No callBackUrl needed for polling approach
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
        
        if status_response:
            # Check if generation is complete
            if 'data' in status_response:
                for item in status_response['data']:
                    if item.get('status') == 'complete' or item.get('audio_url'):
                        return {
                            "success": True,
                            "status": "complete",
                            "data": status_response
                        }
                    elif item.get('status') == 'failed':
                        return {
                            "success": False,
                            "status": "failed",
                            "error": "Music generation failed",
                            "data": status_response
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
    """Check the status of music generation by task ID"""
    
    if request.method == 'GET':
        try:
            status_response = check_generation_status(task_id)
            
            if not status_response:
                return JsonResponse({
                    'success': False,
                    'error': 'Could not fetch status'
                }, status=500)
            
            # Check completion status
            is_complete = False
            is_failed = False
            audio_urls = []
            
            if 'data' in status_response:
                for item in status_response['data']:
                    if item.get('status') == 'complete' or item.get('audio_url'):
                        is_complete = True
                        if item.get('audio_url'):
                            audio_urls.append(item.get('audio_url'))
                    elif item.get('status') == 'failed':
                        is_failed = True
            
            return JsonResponse({
                'success': True,
                'task_id': task_id,
                'is_complete': is_complete,
                'is_failed': is_failed,
                'audio_urls': audio_urls,
                'raw_response': status_response
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

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
            
            return JsonResponse({
                'success': completion_result['success'],
                'task_id': task_id,
                'generated_prompt': generated_prompt,
                'initial_response': generation_result["initial_response"],
                'final_result': completion_result,
                'status': completion_result.get('status'),
                'audio_urls': []  # Extract from completion_result if available
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
