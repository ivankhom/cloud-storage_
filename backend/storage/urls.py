from django.urls import path

from . import views

urlpatterns = [
    path("", views.file_list_view, name="file-list"),
    path("upload/", views.file_upload_view, name="file-upload"),
    path("<int:file_id>/", views.file_delete_view, name="file-delete"),
    path("<int:file_id>/rename/", views.file_rename_view, name="file-rename"),
    path("<int:file_id>/comment/", views.file_comment_view, name="file-comment"),
    path("<int:file_id>/link/", views.file_regenerate_link_view, name="file-link"),
    path("<int:file_id>/download/", views.file_download_view, name="file-download"),
]
