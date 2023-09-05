from django.urls import path
from . import views
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("join", views.join, name="join"),
    path("join/password", views.password, name="password"),
    path("last", views.last, name="last"),
    path("room/<str:room_id>", views.room, name="room"),
    path("room/<str:room_id>/<int:messages>", views.room, name="room"),
    path('favicon.ico', RedirectView.as_view(url=static('favicon.ico'))),
] 