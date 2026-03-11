import json

from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def success_response(data, status=200):
    """API 성공 응답 포맷."""
    return Response({"success": True, "data": data}, status=status)


@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    """
    회원가입 API
    요청 body (JSON): { "id": "사용자아이디", "pw": "비밀번호" }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "유효한 JSON이 아닙니다."},
            status=400,
        )

    user_id = data.get("id")
    password = data.get("pw")

    if not user_id:
        return JsonResponse(
            {"success": False, "message": "id를 입력해주세요."},
            status=400,
        )
    if not password:
        return JsonResponse(
            {"success": False, "message": "pw를 입력해주세요."},
            status=400,
        )

    if User.objects.filter(username=user_id).exists():
        return JsonResponse(
            {"success": False, "message": "이미 사용 중인 아이디입니다."},
            status=400,
        )

    try:
        User.objects.create_user(username=user_id, password=password)
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=400,
        )

    return JsonResponse(
        {"success": True, "message": "회원가입이 완료되었습니다."},
        status=201,
    )


class LoginView(APIView):
    """
    로그인 API (id, pw)
    요청 body: { "id": "사용자아이디", "pw": "비밀번호" }
    성공 시: access_token, refresh_token 반환
    """
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("id")
        password = request.data.get("pw")

        if not user_id:
            return Response(
                {"success": False, "message": "id를 입력해주세요."},
                status=400,
            )
        if not password:
            return Response(
                {"success": False, "message": "pw를 입력해주세요."},
                status=400,
            )

        user = authenticate(request, username=user_id, password=password)
        if user is None:
            return Response(
                {"success": False, "message": "아이디 또는 비밀번호가 올바르지 않습니다."},
                status=401,
            )

        refresh = RefreshToken.for_user(user)
        return success_response(
            {
                "user": {"id": user.id},
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
        )
