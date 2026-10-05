from rest_framework import serializers

from .models import UserFile


class UserFileSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = UserFile
        fields = [
            "id", "original_name", "comment", "size",
            "uploaded_at", "last_downloaded_at", "link_token", "owner_username",
        ]
        read_only_fields = fields
