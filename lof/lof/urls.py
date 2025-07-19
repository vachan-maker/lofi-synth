from django.contrib import admin
from django.urls import path
from lof import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/',views.hello)
]
