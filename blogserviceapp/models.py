from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class Post(models.Model):
    image = models.ImageField(upload_to='blog_images/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

class Comment(models.Model):
    description = models.TextField()
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_messages')
    sender = models.ManyToManyField(User, related_name='sent_messages')
    description = models.TextField()
    send_data = models.DateTimeField(auto_now_add=True)

class BlockedUser(models.Model):
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_users')
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking_users')