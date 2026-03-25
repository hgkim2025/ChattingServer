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


class RoomSearchView(APIView):
    """채팅방 이름 부분 일치 검색."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q") or request.query_params.get("name")
        if not q or not str(q).strip():
            return error_response(
                "검색어를 입력해주세요. (쿼리 파라미터 q 또는 name)",
                status.HTTP_400_BAD_REQUEST,
            )
        rooms = Room.objects.filter(name__icontains=q.strip()).order_by("-created_at")
        serializer = RoomSerializer(rooms, many=True)
        return success_response(serializer.data)


class RoomJoinView(APIView):
    """채팅방 참여. room_id·user_id는 본문(JSON). user_id는 토큰 유저와 일치해야 함."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_id = request.data.get("room_id")
        user_id = request.data.get("user_id")
        if room_id is None or user_id is None:
            return error_response(
                "room_id와 user_id를 입력해주세요.",
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            room_id = int(room_id)
            user_id = int(user_id)
        except (TypeError, ValueError):
            return error_response(
                "room_id와 user_id는 정수여야 합니다.",
                status.HTTP_400_BAD_REQUEST,
            )
        if user_id != request.user.id:
            return error_response(
                "본인 계정으로만 참여할 수 있습니다.",
                status.HTTP_403_FORBIDDEN,
            )
        try:
            room = Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return error_response(
                "존재하지 않는 채팅방입니다.",
                status.HTTP_404_NOT_FOUND,
            )
        member, created = RoomMember.objects.get_or_create(
            room=room,
            user=request.user,
        )
        data = {
            "room": RoomSerializer(room).data,
            "already_member": not created,
        }
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return success_response(data, status_code=code)
