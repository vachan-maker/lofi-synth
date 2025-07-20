from django.urls import path
from .views import upload_image, check_music_status, generate_and_wait, check_multiple_tasks

urlpatterns = [
    path('upload/', upload_image, name='upload-image'),
]