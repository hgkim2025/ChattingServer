from django.urls import path

from . import views

urlpatterns = [
    path("rooms/search/", views.RoomSearchView.as_view(), name="room-search"),
    path("rooms/join/", views.RoomJoinView.as_view(), name="room-join"),
    path("rooms/", views.RoomListCreateView.as_view(), name="room-list-create"),
]
