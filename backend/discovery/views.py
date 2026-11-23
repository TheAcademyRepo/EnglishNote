from datetime import timedelta

from django.db.models import (
    Q,
    Count,
    OuterRef,
    Subquery,
    IntegerField,
    Value,
    F,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date

from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from publishing.models import ContentItem
from engagement.models import Like, Comment, Share

from app.models import Category, Topic

from .serializers import DiscoveryContentSerializer
from .pagination import DiscoveryPagination


def public_content_queryset():

    return ContentItem.objects.filter(
        status=ContentItem.Status.PUBLISHED,
        published_at__isnull=False,
        published_at__lte=timezone.now()
    ).select_related(
        "author",
        "category",
        "topic"
    )


class SearchContentView(generics.ListAPIView):

    serializer_class = DiscoveryContentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DiscoveryPagination

    def get_queryset(self):

        queryset = public_content_queryset()

        params = self.request.query_params

        search = params.get("q", "").strip()

        content_type = params.get("type")
        category = params.get("category")
        topic = params.get("topic")

        date_from = params.get("date_from")
        date_to = params.get("date_to")

        ordering = params.get("ordering", "newest")

        if len(search) > 200:
            raise ValidationError({
                "q": "Search query cannot exceed 200 characters."
            })

        if search:

            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(body__icontains=search)
            )

        if content_type:

            valid_types = [
                choice[0]
                for choice in ContentItem.ContentType.choices
            ]

            if content_type not in valid_types:
                raise ValidationError({
                    "type": "Invalid content type."
                })

            queryset = queryset.filter(
                content_type=content_type
            )

        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        if topic:
            queryset = queryset.filter(
                topic__slug=topic
            )

        if date_from:

            parsed_from = parse_date(date_from)

            if not parsed_from:
                raise ValidationError({
                    "date_from": "Use YYYY-MM-DD format."
                })

            queryset = queryset.filter(
                published_at__date__gte=parsed_from
            )

        if date_to:

            parsed_to = parse_date(date_to)

            if not parsed_to:
                raise ValidationError({
                    "date_to": "Use YYYY-MM-DD format."
                })

            queryset = queryset.filter(
                published_at__date__lte=parsed_to
            )

        if date_from and date_to:

            if parsed_from > parsed_to:
                raise ValidationError({
                    "date_to": "End date cannot be earlier than start date."
                })

        allowed_ordering = {

            "newest": "-published_at",

            "oldest": "published_at",

            "most_viewed": "-views",

            "title": "title",

        }

        if ordering not in allowed_ordering:

            raise ValidationError({
                "ordering": "Invalid ordering option."
            })

        return queryset.order_by(
            allowed_ordering[ordering]
        )


class TrendingContentView(generics.ListAPIView):

    serializer_class = DiscoveryContentSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    pagination_class = DiscoveryPagination

    def get_queryset(self):

        period = self.request.query_params.get(
            "period",
            "7d"
        )

        periods = {

            "24h": timedelta(hours=24),

            "7d": timedelta(days=7),

            "30d": timedelta(days=30),

        }

        if period not in periods:

            raise ValidationError({
                "period": "Use 24h, 7d or 30d."
            })

        start_date = timezone.now() - periods[period]

        queryset = public_content_queryset().filter(
            published_at__gte=start_date
        )

        likes_subquery = (
            Like.objects
            .filter(content_id=OuterRef("pk"))
            .values("content_id")
            .annotate(total=Count("id"))
            .values("total")[:1]
        )

        comments_subquery = (
            Comment.objects
            .filter(
                content_id=OuterRef("pk"),
                is_hidden=False
            )
            .values("content_id")
            .annotate(total=Count("id"))
            .values("total")[:1]
        )

        shares_subquery = (
            Share.objects
            .filter(content_id=OuterRef("pk"))
            .values("content_id")
            .annotate(total=Count("id"))
            .values("total")[:1]
        )

        queryset = queryset.annotate(

            likes_count=Coalesce(
                Subquery(
                    likes_subquery,
                    output_field=IntegerField()
                ),
                Value(0)
            ),

            comments_count=Coalesce(
                Subquery(
                    comments_subquery,
                    output_field=IntegerField()
                ),
                Value(0)
            ),

            shares_count=Coalesce(
                Subquery(
                    shares_subquery,
                    output_field=IntegerField()
                ),
                Value(0)
            ),

        )

        queryset = queryset.annotate(

            trending_score=ExpressionWrapper(

                F("views")
                + F("likes_count") * 3
                + F("comments_count") * 4
                + F("shares_count") * 5,

                output_field=IntegerField()

            )

        )

        return queryset.order_by(
            "-trending_score",
            "-published_at"
        )


class DiscoveryFiltersView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    def get(self, request):

        categories = Category.objects.all().values(
            "id",
            "name",
            "slug"
        )

        topics = Topic.objects.all().values(
            "id",
            "name",
            "slug",
            "subject_id"
        )

        return Response({

            "content_types": [

                {
                    "value": "blog",
                    "label": "Blog"
                },

                {
                    "value": "post",
                    "label": "Post"
                },

                {
                    "value": "daily",
                    "label": "Daily Post"
                },

            ],

            "categories": list(categories),

            "topics": list(topics),

            "ordering": [

                "newest",

                "oldest",

                "most_viewed",

                "title"

            ],

        })