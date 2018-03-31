from django.shortcuts import render, redirect
from . import models
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
import uuid
from django.contrib.auth.views import login_required


def redirect_view(request):
	"""This view will redirect '/' url endpoint to the '/gallery' endpoint"""

	return redirect("/gallery/")


def gallery(request):
	"""The gallery view showing all the albums. It fetches all the albums
	from the database and sends to the template. It uses a generic HTML template
	for rendering"""

	albums = models.Album.objects.all()
	return render(request, 'template/gallery.html', {"albums": albums})


def join(request):
	"""The signup or join view to become a publisher.

	Below are the step by step functions of this controller view:

	When new user submits joining info, this view will do this things step by step:

	01. Checks if the username is already registered or not
	02. If registered, it will give an error message to the user and halt the process
	03. Otherwise, it will check if the password and confirm password data matches or not
	04. If not matches, it will give an error message to the user and halt the process
	05. Otherwise, it will create a new user with that username
	06. Then it hashes the raw password and stores it into the database"""

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
	"""The login or sign in view to make albums.

		Below are the step by step functions of this controller view:

		When new user submits login data, this view will do this things step by step:

		01. It checks if the user is authenticated by checking username and password
		02. If not authenticated(not registered or password error), it will give an
			error message to the user and halt the process
		03. Otherwise, it will login the user by storing the user to a session
		04. If not matches, it will give an error message to the user and halt the process"""

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
	"""The dashboard view for a publisher. It shows all the published albums of the user"""

	albums = models.Album.objects.filter(publisher=request.user.id)
	host = request.get_host()
	return render(request, "template/dashboard.html", {"albums": albums, "host": host})


@login_required(login_url="/login/")
def album_create(request):
	"""The view for creating album.

			Below are the step by step functions of this controller view:

			When new user submits album data, this view will do this things step by step:

			01. It checks if the album name is already taken and shows appropriate message to the user
			02. Then it generates an unique url id for the album by using the awesome python uuid library
			03. Then it will create a new album with the provided data and the generated url id"""

	if request.method == "POST":
		check_album_name = models.Album.objects.filter(name=request.POST["album_name"])

		if check_album_name:
			messages.error(request, "Album already exists, pick a new name")
			return render(request, "template/album_create.html", {})
		else:
			uid = uuid.uuid4().hex
			new_album = models.Album.objects.create(
				publisher=request.user,
				name=request.POST["album_name"],
				album_url_id=uid[:10],
				album_password=request.POST["album_password"]
			)
			return redirect("/dashboard/")
	return render(request, "template/album_create.html", {})


def album_detail(request, uid):
	"""The view for viewing an album.

		Below are the step by step functions of this controller view:

		01. It fetches the album by using the album specific url id and the rating for the album
		02. Then it calculates average rating for the album
		03. When a user first hit the url for an album, the system will check if the user is
			the publisher of this album. If yes, then the system will allow him to view the album
			without password. Cause it's his property.
		04. If this is not the case, then it checks if the user already provided password by
			checking the session. If yes, then it will not ask for password again for the current
			session of the user
		05. If not, then system will redirect the user to the album login page to enter album
			specific password to access it
		"""

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
	"""The view for authorizing user to view an album.

			Below are the step by step functions of this controller view:

			01. It fetches the album by using the album specific url id
			02. Then it checks if the password entered by the viewer matches or not. If yes, then
				system will store this album to session so that user doesn't have to provide password
				again and again for a running session
			03. If not, then the system will give user an error message and halt ther process
			"""

	album = models.Album.objects.get(album_url_id=uid)
	if request.method == "POST":
		if request.POST["_pass"] != album.album_password:
			messages.error(request, "Password error")
			return render(request, "template/album_login.html", {})
		else:
			request.session["album"] = uid
			return redirect("/album/view/%s/" % uid)
	return render(request, "template/album_login.html", {})


@login_required(login_url="/login/")
def add_photos(request, uid):
	"""The view for adding photo to an album.

			Below are the step by step functions of this controller view:

			It stores all the information for a given photo to the database to an actual album as parent
			"""

	if request.method == "POST":
		new_photo = models.Photo.objects.create(
			name=request.POST["photo_name"],
			image=request.FILES["photo"],
			album=models.Album.objects.get(album_url_id=uid)
		)
		messages.success(request, "Photo Added")
		return redirect("/album/view/%s/" % uid)
	return render(request, "template/add_photos.html", {})


def add_comment_rating(request, uid):
	"""The view for adding comment and rating to an album.

		It stores comment and rating data to a specific album.

		 It also checks if the user who comments/rates is registered or not.
		 If registered, then store the user as commenter/rater. Otherwise commenter/rater will be Annonymous

		 The template will check if the viewer is the actual publisher of the album, if he is, then the template will hide
		 comment/rating form. Cause a publisher can not comment or rate his own album"""

	if request.method == "POST":
		new_comment = models.Comment.objects.create(
			comment_text=request.POST["comment"],
			album=models.Album.objects.get(album_url_id=uid)
		)

		new_rating = models.Rate.objects.create(
			rating=request.POST["rating"],
			album=models.Album.objects.get(album_url_id=uid)
		)
		if str(request.user) == "AnnonymousUser":
			new_comment.commenter = request.user
			new_rating.rater = request.user
			new_comment.save()
		messages.success(request, "Comment Added")
		return redirect(request.META["HTTP_REFERER"])


def logout_view(request):
	"""View for log out, it deletes the user from the session"""

	logout(request)
	return redirect("/login/")
