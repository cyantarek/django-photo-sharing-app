from django.db import models
from django.contrib.auth.models import User
import uuid


class Album(models.Model):
	"""
		Album model for storing album data.
		This includes:
		1. the publisher of the album,
		2. An unique URL for the album
		3. Password for viewing the album
		4. And name of the album
	"""

	publisher = models.ForeignKey(User, on_delete=models.CASCADE)
	album_url_id = models.CharField(max_length=10, blank=True, null=True)
	album_password = models.CharField(max_length=15, blank=True, null=True)
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class Photo(models.Model):
	"""
		Photo model for storing photos.
		This includes:
		1. the album where the photo will go to
		2. the actual image file
		3. And name of the photo
	"""

	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	image = models.ImageField(upload_to="images/")
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class Comment(models.Model):
	"""
		Comment model for storing comments.
		This includes:
		1. the album where the comment will go to,
		2. The name of the commenter
		3. And the actual comment text
	"""

	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	comment_text = models.TextField()

	def __str__(self):
		return self.comment_text[:10]


class Rate(models.Model):
	"""
			Rating model for storing ratings.
			This includes:
			1. the album where the rating will be for,
			2. The name of the rater
			3. And the actual rating value
		"""
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	rating = models.IntegerField(default=0)
	rater = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
