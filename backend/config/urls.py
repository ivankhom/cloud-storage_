from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import Http404
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve as static_serve

from storage.views import file_public_download_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/files/", include("storage.urls")),
    path("api/public/<str:token>/", file_public_download_view, name="public-download"),
]

FRONTEND_BUILD_DIR = Path(settings.BASE_DIR) / "frontend_build"

spa_index_view = TemplateView.as_view(template_name="index.html")


def frontend_view(request, path=""):
    """Отдаёт файл сборки фронтенда, а для маршрутов SPA — index.html."""
    if path:
        try:
            return static_serve(request, path, document_root=FRONTEND_BUILD_DIR)
        except Http404:
            if Path(path).suffix:
                raise
    return spa_index_view(request)


if (FRONTEND_BUILD_DIR / "index.html").exists():
    urlpatterns += [
        re_path(r"^(?!api/|admin/|static/)(?P<path>.*)$", frontend_view, name="spa"),
    ]
