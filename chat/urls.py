from django.urls import path

from . import views

urlpatterns = [
    path("rooms/", views.RoomListCreateView.as_view(), name="room-list-create"),
]
