from django.shortcuts import render, redirect

# Create your views here.

from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from .models import Message, Room
from django.utils.encoding import uri_to_iri, iri_to_uri


maxAge = 1 * 24 * 60 * 60 * 60

def get_post(request):
    room_id, username, password = None, None, None
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        if request.POST.get('password') != None:
            password = iri_to_uri(request.POST.get('password').strip())
        if request.POST.get('username') != None:
            username = iri_to_uri(request.POST.get('username').strip())
    if request.method == "GET":
        room_id = request.GET.get('room_id')
        if request.GET.get('password') != None:
            password = iri_to_uri(request.GET.get('password').strip())
        if request.GET.get('username') != None:
            username = iri_to_uri(request.GET.get('username').strip())
    return room_id, username, password

def cookies(request):
    room_id = request.COOKIES.get('room_id')
    username = uri_to_iri(request.COOKIES.get('username'))
    password = uri_to_iri(request.COOKIES.get('password'))
    return room_id, username, password

def index(request):
    context = {}
    if request.COOKIES.get('room_id'):
        context = {"last": request.COOKIES.get('room_id')}
    return render(request, "index.html", context)

def create(request):  # sourcery skip: use-named-expression
    if request.method == "GET":
        return render(request, "create.html")
    room_id, username, password = get_post(request)
    room_name = request.POST.get('room_name').strip()
    if room_name == '':
        context = {
            "error": "Требуется название комнаты!"
        }
        return render(request, "create.html", context)
    if username == '':
        context = {
            "error": "Требуется имя!"
        }
        return render(request, "create.html", context)
    
    is_exist = Room.objects.filter(name=room_name).exists()
    if is_exist: 
        context = {
            "error": "Комната существует!"
        }
        return render(request, "create.html", context) 
    
    room = Room(name=room_name, password=uri_to_iri(password))
    room.save()
    response = redirect("room", room_id=room.id)
    response.set_cookie("room_id", room.id, max_age = maxAge)
    response.set_cookie("username", username, max_age = maxAge)
    response.set_cookie("password", password, max_age = maxAge)
    return response

def join(request):
    if request.method == "GET":
        return render(request, "join.html")
    room_id, username, password = get_post(request)
    room_name = request.POST.get('room_name').strip()
    if room_name == '':
        context = {
            "error": "Требуется название комнаты!"
        }
        return render(request, "join.html", context)
    if username == '':
        context = {
            "error": "Требуется имя!"
        }
        return render(request, "join.html", context)
    room = Room.objects.filter(name=room_name)
    if not room.exists(): 
        context = {
            "error": "Комната не существует!"
        }
        return render(request, "join.html", context) 
    
    response = redirect("room", room_id=room[0].id)
    if room.get().password != '':
        response = redirect("password")
    response.set_cookie("room_id", room[0].id, max_age = maxAge)
    response.set_cookie("username", username, max_age = maxAge)
    return response
    

def room(request, room_id, messages=5):
    room_id, username, password = cookies(request)
    
    if password is None:
        password = ''
    if room_id is None or username is None:
        return redirect("index")

    room = Room.objects.filter(id=room_id)
    if password != room[0].password:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        m = Message(message_text=request.POST.get('message').strip(), pub_date=timezone.now(), room_id=room_id, sender=username)
        m.save()
        
    latest_message_list = Message.objects.filter(room__id=room_id).order_by("-pub_date")[:messages]
    full_message_list = Message.objects.filter(room__id=room_id)
    context = {
        "latest_message_list": latest_message_list,
        "room_id": room_id,
        "room_name": room[0].name,
        "username": username,
        "messages": messages,
        "messages_all": full_message_list.count()
    }
    return render(request, "room.html", context)

def password(request):
    if request.method == "GET":
        return render(request, "password.html")
    room_id = request.COOKIES.get('room_id')
    password = request.POST.get('password').strip()
    room = Room.objects.filter(id=room_id)

    if password != room[0].password:
        context = {
            "error": "Неверный пароль!"
        }
        return render(request, "password.html", context)
    
    response = redirect("room", room_id=room_id)
    response.set_cookie("password", iri_to_uri(password), max_age = maxAge)
    return response

def last(request):
    room_id = request.COOKIES.get('room_id')
    return redirect("room", room_id=room_id)
