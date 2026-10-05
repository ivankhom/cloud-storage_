from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField("Полное имя", max_length=255)
    email = models.EmailField("Email", unique=True)
    is_admin = models.BooleanField("Администратор", default=False)
    storage_path = models.CharField(
        "Путь к хранилищу", max_length=255, unique=True, blank=True
    )

    REQUIRED_FIELDS = ["email", "full_name"]

    def save(self, *args, **kwargs):
        if not self.storage_path:
            self.storage_path = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
