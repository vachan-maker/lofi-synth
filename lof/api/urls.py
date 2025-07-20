from django.urls import path
from .views import upload_image,music_callback

urlpatterns = [
    path('upload/', upload_image, name='upload-image'),
    path('status/<str:task_id>/', check_music_status, name='check-music-status'),
    path('generate-and-wait/', generate_and_wait, name='generate-and-wait'),
]