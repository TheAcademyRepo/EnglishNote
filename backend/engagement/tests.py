from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from app.role_models import RoleAssignment
from app.roles import UserRole

from publishing.models import ContentItem

from .models import Like, Bookmark, Comment


User = get_user_model()


class EngagementTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123!",
            email_verified=True,
        )

        RoleAssignment.objects.update_or_create(
            user=self.user,
            defaults={"role": UserRole.STUDENT}
        )

        self.content = ContentItem.objects.create(
            content_type="blog",
            title="Learning Python",
            body="Python educational content.",
            author=self.user,
            status=ContentItem.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_user_can_like_content(self):

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"/api/engagement/content/{self.content.id}/like/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Like.objects.filter(
                user=self.user,
                content=self.content,
            ).exists()
        )

    def test_user_can_bookmark_content(self):

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"/api/engagement/content/{self.content.id}/bookmark/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Bookmark.objects.filter(
                user=self.user,
                content=self.content,
            ).exists()
        )

    def test_user_can_comment(self):

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"/api/engagement/content/{self.content.id}/comments/",
            {
                "body": "This is a useful article."
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Comment.objects.filter(
                content=self.content,
                user=self.user,
            ).exists()
        )