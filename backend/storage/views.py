import logging
import mimetypes
import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import UserFile, generate_link_token
from .serializers import UserFileSerializer

logger = logging.getLogger("app")
User = get_user_model()

STORED_NAME_ATTEMPTS = 5


def _is_admin(user):
    return user.is_admin or user.is_superuser


def _resolve_target_owner(request):
    """Владелец хранилища: сам пользователь либо ?user=<id> для администратора."""
    user_id = request.query_params.get("user") or request.data.get("user")
    if not user_id:
        return request.user, None

    if not _is_admin(request.user):
        return None, Response(
            {"error": "Доступ к чужому хранилищу разрешён только администратору."},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        owner = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None, Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
    return owner, None


def _absolute_path(user_file):
    return os.path.join(str(settings.STORAGE_ROOT), user_file.owner.storage_path, user_file.stored_name)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def file_list_view(request):
    owner, err = _resolve_target_owner(request)
    if err:
        return err
    files = UserFile.objects.filter(owner=owner)
    return Response(UserFileSerializer(files, many=True).data)


def _generate_stored_name(original_name):
    ext = ""
    if "." in original_name:
        ext = original_name.rsplit(".", 1)[-1][:20]
    return f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex


def _write_upload(upload, user_dir):
    """Сохраняет файл на диск под уникальным именем, не перезаписывая существующие."""
    for _ in range(STORED_NAME_ATTEMPTS):
        stored_name = _generate_stored_name(upload.name)
        full_path = os.path.join(user_dir, stored_name)
        if UserFile.objects.filter(stored_name=stored_name).exists() or os.path.exists(full_path):
            continue
        try:
            dest = open(full_path, "xb")
        except FileExistsError:
            continue
        try:
            with dest:
                for chunk in upload.chunks():
                    dest.write(chunk)
        except OSError:
            if os.path.exists(full_path):
                os.remove(full_path)
            raise
        return stored_name, full_path
    raise OSError("Не удалось подобрать уникальное имя файла.")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def file_upload_view(request):
    owner, err = _resolve_target_owner(request)
    if err:
        return err

    upload = request.FILES.get("file")
    if not upload:
        return Response({"error": "Файл не передан."}, status=status.HTTP_400_BAD_REQUEST)

    if upload.size > settings.MAX_UPLOAD_SIZE:
        return Response(
            {"error": f"Файл превышает максимально допустимый размер "
                      f"({settings.MAX_UPLOAD_SIZE // (1024 * 1024)} МБ)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    comment = request.data.get("comment", "")

    user_dir = os.path.join(str(settings.STORAGE_ROOT), owner.storage_path)
    os.makedirs(user_dir, exist_ok=True)

    try:
        stored_name, full_path = _write_upload(upload, user_dir)
    except OSError:
        logger.exception("File upload failed: %s (owner=%s)", upload.name, owner.username)
        return Response(
            {"error": "Не удалось сохранить файл на сервере."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user_file = UserFile.objects.create(
        owner=owner,
        original_name=upload.name,
        stored_name=stored_name,
        comment=comment,
        size=upload.size,
    )
    logger.info("File uploaded: %s -> %s (owner=%s, by=%s)",
                upload.name, stored_name, owner.username, request.user.username)
    return Response(UserFileSerializer(user_file).data, status=status.HTTP_201_CREATED)


def _get_owned_file(request, file_id):
    """Возвращает (user_file, error) с проверкой прав доступа."""
    try:
        user_file = UserFile.objects.select_related("owner").get(id=file_id)
    except UserFile.DoesNotExist:
        return None, Response({"error": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)

    if user_file.owner_id != request.user.id and not _is_admin(request.user):
        return None, Response({"error": "Нет доступа к этому файлу."}, status=status.HTTP_403_FORBIDDEN)

    return user_file, None


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def file_delete_view(request, file_id):
    user_file, err = _get_owned_file(request, file_id)
    if err:
        return err

    path = _absolute_path(user_file)
    if os.path.exists(path):
        os.remove(path)
    name = user_file.original_name
    user_file.delete()
    logger.info("File deleted: %s (id=%s) by %s", name, file_id, request.user.username)
    return Response({"message": "Файл удалён."})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def file_rename_view(request, file_id):
    user_file, err = _get_owned_file(request, file_id)
    if err:
        return err

    new_name = (request.data.get("name") or "").strip()
    if not new_name:
        return Response({"error": "Новое имя файла обязательно."}, status=status.HTTP_400_BAD_REQUEST)

    user_file.original_name = new_name
    user_file.save(update_fields=["original_name"])
    logger.info("File renamed to '%s' (id=%s) by %s", new_name, file_id, request.user.username)
    return Response(UserFileSerializer(user_file).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def file_comment_view(request, file_id):
    user_file, err = _get_owned_file(request, file_id)
    if err:
        return err

    user_file.comment = request.data.get("comment", "")
    user_file.save(update_fields=["comment"])
    logger.info("File comment updated (id=%s) by %s", file_id, request.user.username)
    return Response(UserFileSerializer(user_file).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def file_regenerate_link_view(request, file_id):
    user_file, err = _get_owned_file(request, file_id)
    if err:
        return err
    user_file.link_token = generate_link_token()
    user_file.save(update_fields=["link_token"])
    return Response(UserFileSerializer(user_file).data)


def _serve_file(user_file):
    path = _absolute_path(user_file)
    if not os.path.exists(path):
        raise Http404("Файл отсутствует на диске.")
    content_type, _ = mimetypes.guess_type(user_file.original_name)
    user_file.last_downloaded_at = timezone.now()
    user_file.save(update_fields=["last_downloaded_at"])
    response = FileResponse(
        open(path, "rb"), as_attachment=True, filename=user_file.original_name,
        content_type=content_type or "application/octet-stream",
    )
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def file_download_view(request, file_id):
    user_file, err = _get_owned_file(request, file_id)
    if err:
        return err
    logger.info("File downloaded: %s (id=%s) by %s", user_file.original_name, file_id, request.user.username)
    return _serve_file(user_file)


@api_view(["GET"])
@permission_classes([AllowAny])
def file_public_download_view(request, token):
    try:
        user_file = UserFile.objects.get(link_token=token)
    except UserFile.DoesNotExist:
        raise Http404("Ссылка недействительна.")
    logger.info("File downloaded via public link: %s (id=%s)", user_file.original_name, user_file.id)
    return _serve_file(user_file)
