from django.urls import path
from . import views

urlpatterns = [
	path("", views.redirect_view),
	path("login/", views.login_view),
	path("logout/", views.logout_view),
	path("gallery/", views.gallery),
	path("join/", views.join),
	path("dashboard/", views.dashboard),
	path("album/create/", views.album_create),
	path("album/<str:uid>/add_photos/", views.add_photos),
	path("album/<str:uid>/comment/", views.add_comment),
	path("album/view/<str:uid>/", views.album_detail),
	path("album/login/<str:uid>/", views.album_login),
]
