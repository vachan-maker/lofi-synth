from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse


@api_view(['GET'])
def hello(request):
    return Response({'message': 'Hello from Django!'})

# my_app/views.py
from django.http import JsonResponse

def hello_api_view(request):
    # This dictionary will be converted to JSON
    data = {
        'message': 'Hello from your Django API! 👋'
    }
    return JsonResponse(data)