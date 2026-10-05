from django.db import migrations

from config import app_settings as app_cfg


def create_default_admin(apps, schema_editor):
    User = apps.get_model("users", "User")
    from django.contrib.auth.hashers import make_password

    if not User.objects.filter(username=app_cfg.DEFAULT_ADMIN_LOGIN).exists():
        User.objects.create(
            username=app_cfg.DEFAULT_ADMIN_LOGIN,
            email=app_cfg.DEFAULT_ADMIN_EMAIL,
            full_name="Администратор",
            password=make_password(app_cfg.DEFAULT_ADMIN_PASSWORD),
            is_admin=True,
            is_staff=True,
            is_superuser=True,
            storage_path=app_cfg.DEFAULT_ADMIN_LOGIN,
        )


def remove_default_admin(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(username=app_cfg.DEFAULT_ADMIN_LOGIN).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
