from django.contrib import admin
from django.urls import path
from lof import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.hello,name="home"),
    path('api/hello/', views.hello_api_view, name='api-hello'),
]
