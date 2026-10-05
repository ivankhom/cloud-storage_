from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.csrf_token_view, name="csrf"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.current_user_view, name="current-user"),
    path("", views.user_list_view, name="user-list"),
    path("<int:user_id>/", views.user_delete_view, name="user-delete"),
    path("<int:user_id>/admin/", views.user_set_admin_view, name="user-set-admin"),
]
