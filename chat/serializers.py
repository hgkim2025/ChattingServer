from rest_framework import serializers

from .models import Room, RoomMember


class RoomSerializer(serializers.ModelSerializer):
    """채팅방 조회용."""

    class Meta:
        model = Room
        fields = ("id", "name", "type", "created_at")

