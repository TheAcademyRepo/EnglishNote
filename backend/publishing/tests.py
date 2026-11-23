from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from app.models import Category
from app.role_models import RoleAssignment
from app.roles import UserRole

from .models import ContentItem


User = get_user_model()


class PublishingTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            email_verified=True,
        )

        RoleAssignment.objects.update_or_create(
            user=self.author,
            defaults={"role": UserRole.AUTHOR}
        )

        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123!",
            email_verified=True,
        )

        RoleAssignment.objects.update_or_create(
            user=self.student,
            defaults={"role": UserRole.STUDENT}
        )

        self.category = Category.objects.create(
            name="Programming",
            slug="programming",
        )

        self.content = ContentItem.objects.create(
            content_type=ContentItem.ContentType.BLOG,
            title="Django Testing",
            body="Learning Django testing.",
            author=self.author,
            category=self.category,
            status=ContentItem.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_public_content_is_accessible(self):

        response = self.client.get(
            "/api/publishing/public/"
        )

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_create_content(self):

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.post(
            "/api/publishing/manage/",
            {
                "content_type": "blog",
                "title": "Unauthorized",
                "body": "This should not be created.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_author_can_view_own_management_content(self):

        self.client.force_authenticate(
            user=self.author
        )

        response = self.client.get(
            "/api/publishing/manage/"
        )

        self.assertEqual(response.status_code, 200)

    def test_public_detail_does_not_require_login(self):

        response = self.client.get(
            f"/api/publishing/public/{self.content.slug}/"
        )

        self.assertEqual(response.status_code, 200)