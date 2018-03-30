from django.shortcuts import render, redirect
from . import models
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
import uuid
from django.contrib.auth.views import login_required


def redirect_view(request):
	return redirect("/gallery/")

def gallery(request):
	albums = models.Album.objects.all()
	return render(request, 'template/gallery.html', {"albums": albums})

def join(request):
	if request.method == "POST":
		check_username = models.User.objects.filter(username=request.POST["username"])
		if check_username:
			messages.error(request, "Username already exists")
			return render(request, "template/signup_page.html", {})
		elif request.POST["password"] != request.POST["confirm_password"]:
			messages.error(request, "Password did not match")
			return render(request, "template/signup_page.html", {})
		else:
			new_user = models.User.objects.create(
				username=request.POST["username"],
			)
			new_user.set_password(request.POST["password"])
			new_user.save()
			return redirect("/login/")
	return render(request, "template/signup_page.html", {})

def login_view(request):
	if request.method == "POST":
		user = authenticate(username=request.POST["username"], password=request.POST["password"])
		if user:
			login(request, user=user)
			return redirect("/dashboard/")
		else:
			messages.error(request, "Login error")
	return render(request, "template/login_page.html", {})

@login_required(login_url="/login/")
def dashboard(request):
	albums = models.Album.objects.filter(publisher=request.user.id)
	return render(request, "template/dashboard.html", {"albums": albums})


@login_required(login_url="/login/")
def album_create(request):
	if request.method == "POST":
		uid = uuid.uuid4().hex
		check_album_name = models.Album.objects.filter(name=request.POST["album_name"])

		if check_album_name:
			messages.error(request, "Album already exists, pick a new name")
			return render(request, "template/album_create.html", {})
		new_album = models.Album.objects.create(
			publisher=request.user,
			name=request.POST["album_name"],
			album_url_id=uid[:10],
			album_password=request.POST["album_password"]
		)
		return redirect("/dashboard/")
	return render(request, "template/album_create.html", {})


def album_detail(request, uid):
	album = models.Album.objects.get(album_url_id=uid)
	rating = models.Rate.objects.filter(album=album)
	total_rating = 0
	avg_rating = 0

	for i in rating:
		total_rating += i.rating

	if rating.count() > 0:
		avg_rating = total_rating / rating.count()
	if request.user != album.publisher:
		if request.session.get("album") != uid or not request.session.get("album"):
			return redirect("/album/login/%s/" % album.album_url_id)
		else:
			return render(request, "template/album_details.html", {"album": album, "rating": avg_rating})
	else:
		return render(request, "template/album_details.html", {"album": album, "rating": avg_rating})

def album_login(request, uid):
	album = models.Album.objects.get(album_url_id=uid)
	if request.method == "POST":
		if request.POST["_pass"] != album.album_password:
			messages.error(request, "Password error")
			return render(request, "template/album_login.html", {})
		else:
			request.session["album"] = uid
			return redirect("/album/view/%s/" % uid)
	return render(request, "template/album_login.html", {})

# @login_required(login_url="/login/")
def add_photos(request, uid):
	print(request.POST)
	if request.method == "POST":
		new_photo = models.Photo.objects.create(
			name=request.POST["photo_name"],
			image=request.FILES["photo"],
			album=models.Album.objects.get(album_url_id=uid),
			is_featured=True if request.POST.get("is_featured") == "on" else False
		)
		messages.success(request, "Photo Added")
		return redirect("/album/view/%s/" % uid)
	return render(request, "template/add_photos.html", {})


def add_comment(request, uid):
	if request.method == "POST":
		new_comment = models.Comment.objects.create(
			comment_text=request.POST["comment"],
			album=models.Album.objects.get(album_url_id=uid)
		)

		new_rating = models.Rate.objects.create(
			rating=request.POST["rating"],
			album=models.Album.objects.get(album_url_id=uid)
		)
		if str(request.user) != "AnnonymousUser":
			new_comment.commenter = request.user
			new_rating.rater=request.user
			new_comment.save()
		messages.success(request, "Comment Added")
		return redirect(request.META["HTTP_REFERER"])

def logout_view(request):
	logout(request)
	return redirect("/login/")
