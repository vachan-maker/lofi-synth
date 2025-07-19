from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from .utils import generate_lofi_prompt

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

        file = request.FILES.get('file')
        print(file)
        filename = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        file_path = os.path.join(default_storage.location, filename)

        try:
            prompt = generate_lofi_prompt(file_path)
            return JsonResponse({'success': True, 'lofi_prompt': prompt})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)
