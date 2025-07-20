# api/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json

from .utils import (
    generate_lofi_prompt,
    submit_music_generation,
    poll_for_completion,
    extract_music_info,
    check_generation_status
)

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        file = request.FILES.get('file')
        filename = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        file_path = os.path.join(default_storage.location, filename)
        try:
            generated_prompt = generate_lofi_prompt(file_path)
            generation_result = submit_music_generation(generated_prompt)
            task_id = generation_result["task_id"]
            return JsonResponse({
                'success': True, 
                'message': 'Music generation started',
                'task_id': task_id,
                'generated_prompt': generated_prompt,
                'initial_response': generation_result["initial_response"]
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

@csrf_exempt
def check_music_status(request, task_id):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Only GET method allowed'}, status=405)
    if not task_id or not task_id.strip():
        return JsonResponse({'success': False, 'error': 'Task ID is required'}, status=400)
    try:
        api_response = check_generation_status(task_id)
        if not api_response:
            return JsonResponse({'success': False, 'error': 'Could not fetch status from Suno API', 'task_id': task_id}, status=500)
        if 'error' in api_response:
            status_code = api_response.get('status_code', 500)
            return JsonResponse({'success': False, 'error': api_response['error'], 'task_id': task_id}, status=status_code)
        music_info = extract_music_info(api_response)
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
            'raw_response': api_response
        }
        if music_info['errors']:
            response_data['errors'] = music_info['errors']
        return JsonResponse(response_data)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e), 'task_id': task_id}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Internal server error: {str(e)}', 'task_id': task_id}, status=500)

@csrf_exempt
def generate_and_wait(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)
        file = request.FILES.get('file')
        filename = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        file_path = os.path.join(default_storage.location, filename)
        try:
            generated_prompt = generate_lofi_prompt(file_path)
            generation_result = submit_music_generation(generated_prompt)
            task_id = generation_result["task_id"]
            completion_result = poll_for_completion(task_id, poll_interval=10, max_wait_time=300)
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
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)

@csrf_exempt 
def check_multiple_tasks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        if not task_ids or not isinstance(task_ids, list):
            return JsonResponse({'success': False, 'error': 'task_ids array is required'}, status=400)
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
                results[task_id] = {'success': False, 'error': str(e)}
        return JsonResponse({
            'success': True,
            'results': results,
            'total_tasks': len(task_ids),
            'successful_checks': len([r for r in results.values() if r.get('success')])
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
