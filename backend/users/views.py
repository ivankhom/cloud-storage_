import logging

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import CurrentUserSerializer, UserPublicSerializer
from .validators import validate_registration

logger = logging.getLogger("app")


def is_admin_user(user):
    return user.is_authenticated and (user.is_admin or user.is_superuser)


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token_view(request):
    token = get_token(request)
    return Response({"csrfToken": token})


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    errors = validate_registration(data)

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()

    if not errors:
        if User.objects.filter(username__iexact=username).exists():
            errors["username"] = "Пользователь с таким логином уже существует."
        if User.objects.filter(email__iexact=email).exists():
            errors["email"] = "Пользователь с таким email уже существует."

    if errors:
        logger.info("Registration validation failed for '%s': %s", username, errors)
        return Response({"error": "Некорректные данные регистрации.", "details": errors},
                         status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=data.get("password"),
        full_name=(data.get("full_name") or "").strip(),
    )
    logger.info("New user registered: %s", user.username)
    django_login(request, user)
    return Response(CurrentUserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""

    if not User.objects.filter(username__iexact=username).exists():
        logger.info("Login failed: unknown user '%s'", username)
        return Response({"error": "Пользователь с таким логином не найден."},
                         status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is None:
        logger.info("Login failed: wrong password for '%s'", username)
        return Response({"error": "Неверный пароль."}, status=status.HTTP_400_BAD_REQUEST)

    django_login(request, user)
    logger.info("User logged in: %s", user.username)
    return Response(CurrentUserSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    username = request.user.username
    django_logout(request)
    logger.info("User logged out: %s", username)
    return Response({"message": "Вы вышли из системы."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    return Response(CurrentUserSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_list_view(request):
    if not is_admin_user(request.user):
        return Response({"error": "Доступ только для администратора."},
                         status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().order_by("username")
    return Response(UserPublicSerializer(users, many=True).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def user_delete_view(request, user_id):
    if not is_admin_user(request.user):
        return Response({"error": "Доступ только для администратора."},
                         status=status.HTTP_403_FORBIDDEN)
    if request.user.id == user_id:
        return Response({"error": "Нельзя удалить самого себя."},
                         status=status.HTTP_400_BAD_REQUEST)
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    target.delete()
    logger.info("User deleted by admin %s: %s", request.user.username, user_id)
    return Response({"message": "Пользователь удалён."})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_set_admin_view(request, user_id):
    if not is_admin_user(request.user):
        return Response({"error": "Доступ только для администратора."},
                         status=status.HTTP_403_FORBIDDEN)
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if request.user.id == user_id:
        return Response({"error": "Нельзя изменить признак администратора у самого себя."},
                         status=status.HTTP_400_BAD_REQUEST)

    target.is_admin = bool(request.data.get("is_admin"))
    target.save(update_fields=["is_admin"])
    logger.info("Admin flag for %s set to %s by %s", target.username, target.is_admin, request.user.username)
    return Response(UserPublicSerializer(target).data)
