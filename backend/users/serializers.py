from rest_framework import serializers

from storage.models import UserFile
from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    """Пользователь без пароля + агрегаты по файловому хранилищу (для админ-списка)."""
    files_count = serializers.SerializerMethodField()
    files_size = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "full_name", "email",
            "is_admin", "date_joined", "files_count", "files_size",
        ]

    def get_files_count(self, obj):
        return UserFile.objects.filter(owner=obj).count()

    def get_files_size(self, obj):
        return sum(UserFile.objects.filter(owner=obj).values_list("size", flat=True))


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "is_admin"]
