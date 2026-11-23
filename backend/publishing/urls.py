from django.urls import path

from .views import (
    ContentListCreateView,
    PublicContentListView,
    ContentDetailView,
    SubmitContentView,
    ReviewContentView,
    PublishContentView,
    ContentViewCountView,
    ContentVersionListView,
    ContentReviewListView,
    PublicContentDetailView
)


urlpatterns = [

    path(
        "public/",
        PublicContentListView.as_view(),
        name="public-content"
    ),

    path(
        "manage/",
        ContentListCreateView.as_view(),
        name="content-manage"
    ),
    path(
    "public/<slug:slug>/",
    PublicContentDetailView.as_view(),
    name="public-content-detail"),

    path(
        "manage/<slug:slug>/",
        ContentDetailView.as_view(),
        name="content-detail"
    ),

    path(
        "<uuid:pk>/submit/",
        SubmitContentView.as_view(),
        name="content-submit"
    ),

    path(
        "<uuid:pk>/review/",
        ReviewContentView.as_view(),
        name="content-review"
    ),

    path(
        "<uuid:pk>/publish/",
        PublishContentView.as_view(),
        name="content-publish"
    ),

    path(
        "<uuid:pk>/view/",
        ContentViewCountView.as_view(),
        name="content-view"
    ),

    path(
        "<uuid:pk>/versions/",
        ContentVersionListView.as_view(),
        name="content-versions"
    ),

    path(
        "reviews/",
        ContentReviewListView.as_view(),
        name="content-reviews"
    ),

]