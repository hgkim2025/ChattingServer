from django.urls import path

from . import views

urlpatterns = [
    path("rooms/", views.RoomCreateView.as_view(), name="room-create"),
]
