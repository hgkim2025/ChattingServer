from django.conf import settings
from django.db import models


class Room(models.Model):
    """채팅방. type으로 DM/그룹 등 구분."""
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # e.g. 'dm', 'group'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_room'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.type})"


class RoomMember(models.Model):
    """방 참여 멤버. 한 유저가 같은 방에 중복 참여 불가."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='room_members',
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='members',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_room_member'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'room'],
                name='unique_user_per_room',
            )
        ]
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user_id} in Room {self.room_id}"


class Message(models.Model):
    """텍스트 메시지. 이미지 등은 추후 확장."""
    TYPE_TEXT = 'text'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'text'),
        # ('image', 'image'),  # 추후 추가
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    content = models.TextField()  # 텍스트 내용
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_TEXT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at'], name='chat_msg_room_created_idx'),
        ]

    def __str__(self):
        return f"Message {self.id} in Room {self.room_id} by {self.user_id}"
