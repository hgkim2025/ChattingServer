from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomMember
from .serializers import RoomSerializer

User = get_user_model()


def success_response(data, status_code=200):
    return Response({"success": True, "data": data}, status=status_code)


def error_response(message, status_code=400):
    return Response({"success": False, "message": message}, status=status_code)


class RoomListCreateView(APIView):
    """GET: 내가 속한 채팅방 목록. POST: 채팅방 생성(생성한 유저는 자동으로 멤버)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(members__user=request.user).distinct().order_by("-created_at")
        serializer = RoomSerializer(rooms, many=True)
        return success_response(serializer.data)

    def post(self, request):
        name = request.data.get("name")
        room_type = "group"

        if not name:
            return error_response("name을 입력해주세요.", status.HTTP_400_BAD_REQUEST)

        room = Room.objects.create(name=name, type=room_type)
        RoomMember.objects.create(room=room, user=request.user)

        data = {
            "id": room.id,
            "name": room.name,
            "type": room.type,
            "created_at": room.created_at,
        }
        return success_response(data, status_code=status.HTTP_201_CREATED)
