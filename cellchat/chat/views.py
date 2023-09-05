from django.shortcuts import render, redirect

# Create your views here.

from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from .models import Message, Room

maxAge = 1 * 24 * 60 * 60 * 60

def index(request):
    context = {}
    if request.COOKIES.get('room_id'):
        context = {"last": request.COOKIES.get('room_id')}
    return render(request, "index.html", context)

def create(request):  # sourcery skip: use-named-expression
    if request.method == "GET":
        return render(request, "create.html")
    
    request.encoding = ('utf-8')
    room_id = request.POST.get('room_id').strip(" ")
    username = request.POST.get('username')
    password = request.POST.get('password').strip(" ")
    
    if room_id == '':
        context = {
            "error": "Требуется название комнаты!"
        }
        return render(request, "create.html", context)
    if username == '':
        context = {
            "error": "Требуется имя!"
        }
        return render(request, "create.html", context)
    
    is_exist = Room.objects.filter(id=room_id).exists()
    if is_exist: 
        context = {
            "error": "Комната существует!"
        }
        return render(request, "create.html", context) 
    
    room = Room(id=room_id, password=password)
    room.save()
    response = redirect("room", room_id=room_id)
    response.set_cookie("room_id", room_id, max_age = maxAge)
    response.set_cookie("username", username, max_age = maxAge)
    response.set_cookie("password", password, max_age = maxAge)
    return response

def join(request):
    if request.method == "GET":
        return render(request, "join.html")

    room_id = request.POST.get('room_id').strip(" ")
    username = request.POST.get('username').strip(" ")
    
    if room_id == '':
        context = {
            "error": "Требуется название комнаты!"
        }
        return render(request, "join.html", context)
    if username == '':
        context = {
            "error": "Требуется имя!"
        }
        return render(request, "join.html", context)
    room = Room.objects.filter(id=room_id)
    is_exist = room.exists()
    if not is_exist: 
        context = {
            "error": "Комната не существует!"
        }
        return render(request, "join.html", context) 
    
    if room.get().password != '':
        response = redirect("password")
        response.set_cookie("room_id", room_id, max_age = maxAge)
        response.set_cookie("username", username, max_age = maxAge)
        return response
    
    response = redirect("room", room_id=room_id)
    response.set_cookie("room_id", room_id, max_age = maxAge)
    response.set_cookie("username", username, max_age = maxAge)
    return response
    

def room(request, room_id, messages=5):
    username = request.COOKIES.get('username')
    password = request.COOKIES.get('password')
    if password is None:
        password = ''
    if room_id is None or username is None:
        return redirect("index")
    
    room = Room.objects.filter(id=room_id)
    if password != room.get().password:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        m = Message(message_text=request.POST.get('message'), pub_date=timezone.now(), room_id=room_id, sender=username)
        m.save()
        
    latest_message_list = Message.objects.filter(room__id=room_id).order_by("-pub_date")[:messages]
    full_message_list = Message.objects.filter(room__id=room_id)
    context = {
        "latest_message_list": latest_message_list,
        "room_id": room_id,
        "username": username,
        "messages": messages,
        "messages_all": full_message_list.count()
    }
    return render(request, "room.html", context)

def password(request):
    if request.method == "GET":
        return render(request, "password.html")
    room_id = request.COOKIES.get('room_id')
    password = request.POST.get('password').strip(" ")
    room = Room.objects.filter(id=room_id)

    if password != room.get().password:
        context = {
            "error": "Неверный пароль!"
        }
        return render(request, "password.html", context)
    
    response = redirect("room", room_id=room_id)
    response.set_cookie("password", password, max_age = maxAge)
    return response

def last(request):
    room_id = request.COOKIES.get('room_id')
    return redirect("room", room_id=room_id)