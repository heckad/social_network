from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Post(models.Model):
    author = models.ForeignKey(User, models.CASCADE)
    title = models.CharField(max_length=64)
    content = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    list_display = ('title', 'author', 'created_on', 'updated_on')
    search_fields = ['author', 'title']
    list_filter = ['created_on']
    date_hierarchy = 'pub_date'


class LikeDislike(models.Model):
    LIKE = '+'
    DISLIKE = '-'

    VOTES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Unlike')
    )

    user = models.ForeignKey(User, models.CASCADE, verbose_name="User", related_name='votes')
    post = models.ForeignKey(Post, models.CASCADE, verbose_name="Post", related_name='votes')
    vote = models.CharField(verbose_name="Vote", choices=VOTES, max_length=1)

    class Meta:
        unique_together = ['user', 'post']
