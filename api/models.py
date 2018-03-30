from django.db import models
from django.contrib.auth.models import User
import uuid

class Album(models.Model):
	publisher = models.ForeignKey(User, on_delete=models.CASCADE)
	album_url_id = models.CharField(max_length=10, blank=True, null=True)
	album_password = models.CharField(max_length=15, blank=True, null=True)
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name

	def generate_url(self):
		self.album_url_id = uuid.uuid4()[:5]

class Photo(models.Model):
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	image = models.ImageField(upload_to="images/")
	name = models.CharField(max_length=100)
	is_featured = models.BooleanField(default=False)

	def __str__(self):
		return self.name

class Comment(models.Model):
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	comment_text = models.TextField()

	def __str__(self):
		return self.comment_text[:10]

class Rate(models.Model):
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	rating = models.IntegerField(default=0)
	rater = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
