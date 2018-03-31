from django.urls import path
from . import views

urlpatterns = [
	path("", views.redirect_view), #root url
	path("login/", views.login_view), #login url
	path("logout/", views.logout_view), #logout url
	path("gallery/", views.gallery), #gallery url
	path("join/", views.join), #signup url
	path("dashboard/", views.dashboard), #dashboard
	path("album/create/", views.album_create), #create album url
	path("album/<str:uid>/add_photos/", views.add_photos), #adding photos url
	path("album/<str:uid>/comment_rating/", views.add_comment_rating), #adding comment and rating url
	path("album/view/<str:uid>/", views.album_detail), #viewing album url
	path("album/login/<str:uid>/", views.album_login), #album login url
]
