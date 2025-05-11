from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Post(models.Model):
    
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
    
    class PubishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status=Post.Status.PUBLISHED)
        
        
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    body = models.TextField()
    publish_date = models.DateTimeField(default = timezone.now)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2,
                                choices = Status.choices,
                                default = Status.DRAFT)
    author = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='blog_posts')
    objects = models.Manager()
    published = PubishedManager()
    class Meta:
        ordering = ['-publish_date']
        indexes = [
            models.Index(fields=['-publish_date'])
        ]
    
    def __str__(self):
        return self.title
    
# Create your models here.
