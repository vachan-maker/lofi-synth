from django.urls import path
from .views import upload_image

urlpatterns = [
    path('upload/', upload_image, name='upload-image'),
    path('callback/', music_callback, name='music-callback'),
]