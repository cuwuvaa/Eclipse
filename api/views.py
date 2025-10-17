from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from EclipseUser.models import CustomUser
# Create your views here.

@csrf_exempt
def get_user_data(request, userid):
    user = CustomUser.objects.get(id=userid)
    return JsonResponse({
        'id':userid,
        'username':user.username,
        'avatar':user.avatar.url
        })