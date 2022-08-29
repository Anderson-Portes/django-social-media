import uuid
from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  id_user = models.IntegerField()
  bio = models.TextField(blank=True)
  profile_img = models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
  location = models.CharField(max_length=100, blank=True)

  def __str__(self):
    return self.user.username

class Post(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  image = models.ImageField(upload_to="post_images")
  caption = models.TextField()
  created_at = models.DateTimeField(default=datetime.now)
  number_of_likes = models.IntegerField(default=0)

  def __str__(self):
    return self.caption + " - " + self.user.username

class Like(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.user.username + " liked " + self.post.caption

class Follower(models.Model):
  user = models.TextField()
  follower = models.TextField()

  def __str__(self):
    return self.follower + " is following " + self.user