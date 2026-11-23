import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class ContentItem(models.Model):

    class ContentType(models.TextChoices):
        BLOG = "blog", "Blog Article"
        POST = "post", "Educational Post"
        DAILY = "daily", "Daily Post"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted for Review"
        IN_REVIEW = "in_review", "Under Review"
        REVISION = "revision", "Revision Requested"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        blank=True
    )

    excerpt = models.TextField(
        max_length=500,
        blank=True
    )

    body = models.TextField()

    image = models.ImageField(
        upload_to="publishing/",
        null=True,
        blank=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publishing_items"
    )

    category = models.ForeignKey(
        "app.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publishing_items"
    )

    topic = models.ForeignKey(
        "app.Topic",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publishing_items"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_content"
    )

    review_notes = models.TextField(
        blank=True
    )

    rejection_reason = models.TextField(
        blank=True
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    views = models.PositiveBigIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["content_type", "status"]),
            models.Index(fields=["author", "status"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.title) or "content"

            slug = base_slug
            counter = 1

            while ContentItem.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):

        return self.title


class ContentReview(models.Model):

    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REVISION = "revision", "Revision Requested"

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="content_reviews"
    )

    decision = models.CharField(
        max_length=20,
        choices=Decision.choices
    )

    feedback = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return f"{self.content.title} - {self.decision}"


class ContentVersion(models.Model):

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="versions"
    )

    title = models.CharField(
        max_length=255
    )

    body = models.TextField()

    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return f"{self.content.title} version"