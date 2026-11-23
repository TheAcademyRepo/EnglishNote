from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Q


class User(AbstractUser):
    email = models.EmailField(
        unique=True
    )

    email_verified = models.BooleanField(
        default=False
    )

class Subject (models.Model):
    title = models.CharField (max_length=1000, unique=True)
    slug = models.CharField(max_length=1000, unique=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
      return self.title


class Topic (models.Model):
    name = models.CharField (max_length=1000, unique=True)
    slug = models.CharField(max_length=1000, unique=True, blank=True)
    subject = models.ForeignKey(
      Subject,
    on_delete=models.CASCADE,
    related_name="topics",
    null=True,
    blank=True,
      )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
      return self.name





class Category (models.Model):
    name = models.CharField (max_length=1000, unique=True)
    slug = models.CharField(max_length=1000, unique=True)
    
    
    def __str__(self):
      return self.name
  
class Post (models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(
    max_length=255,
    unique=True,
    blank=True )
    content = CKEditor5Field("Content", config_name="default")
    image = models.ImageField(
      upload_to ="posts/",
      blank = True,
      null = True )
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    category =  models.ForeignKey(
      Category,
      on_delete=models.CASCADE,
      related_name='posts')
      
      
      
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
      return self.title
# Create your models here.


class Note (models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True, blank=True)
    
    content = CKEditor5Field("Content", config_name="default")
    image = models.ImageField(
      upload_to ="posts/",
      blank = True,
      null = True )
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    topic = models.ForeignKey(
      Topic,
      on_delete=models.CASCADE,
      related_name='notes'
      )
      

      
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
      return self.title
      
class Dailypost (models.Model):
  
    title = models.CharField(max_length=15)
    slug = models.SlugField(unique=True)
    content = CKEditor5Field("Content", config_name="default")
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    image = models.ImageField(
      blank = True,
      null = True,
      upload_to ="posts/" )
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
          self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
      return self.title
      
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.post.title}"
        
        
class PostLike(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    visitor_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                condition=Q(user__isnull=False),
                name="unique_user_post_like"
            ),
            models.UniqueConstraint(
                fields=["post", "visitor_id"],
                condition=Q(visitor_id__isnull=False),
                name="unique_visitor_post_like"
            ),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} liked {self.post.title}"

        return "Visitor liked {}".format(self.post.title)

# Create your models here.




# Role and profile models
from .role_models import UserProfile, RoleAssignment