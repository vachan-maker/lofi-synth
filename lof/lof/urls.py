from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from lof import views

def home(request):
    return HttpResponse("API is running. Visit /api/auth/login/")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/auth/',views.login_api),
]
