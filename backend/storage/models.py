import secrets

from django.conf import settings
from django.db import models


def generate_link_token():
    return secrets.token_urlsafe(24)


class UserFile(models.Model):
    """Файл, загруженный пользователем в своё хранилище."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="files", on_delete=models.CASCADE
    )
    original_name = models.CharField("Оригинальное имя файла", max_length=255)
    stored_name = models.CharField("Имя файла на диске", max_length=64, unique=True)
    comment = models.CharField("Комментарий", max_length=500, blank=True, default="")
    size = models.BigIntegerField("Размер (байт)", default=0)
    uploaded_at = models.DateTimeField("Дата загрузки", auto_now_add=True)
    last_downloaded_at = models.DateTimeField("Последнее скачивание", null=True, blank=True)
    link_token = models.CharField(
        "Токен специальной ссылки", max_length=64, unique=True, default=generate_link_token
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_name} ({self.owner})"
