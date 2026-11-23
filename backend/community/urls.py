from django.urls import path

from .views import (
    MyProfileView,
    PublicProfileView,
    FollowToggleView,
    FollowersListView,
    FollowingListView,
    AuthorContentView,
    AuthorStatisticsView,
    SuggestedAuthorsView,
    PersonalizedFeedView,
)


urlpatterns = [

    # Personal profile
    path(
        "profile/me/",
        MyProfileView.as_view(),
        name="my-profile"
    ),

    # Public profile
    path(
        "profile/<str:username>/",
        PublicProfileView.as_view(),
        name="public-profile"
    ),

    # Follow and unfollow
    path(
        "follow/<str:username>/",
        FollowToggleView.as_view(),
        name="follow-toggle"
    ),

    # Followers
    path(
        "profile/<str:username>/followers/",
        FollowersListView.as_view(),
        name="followers-list"
    ),

    # Following
    path(
        "profile/<str:username>/following/",
        FollowingListView.as_view(),
        name="following-list"
    ),

    # Author content
    path(
        "profile/<str:username>/content/",
        AuthorContentView.as_view(),
        name="author-content"
    ),

    # Author statistics
    path(
        "profile/<str:username>/statistics/",
        AuthorStatisticsView.as_view(),
        name="author-statistics"
    ),

    # Suggested authors
    path(
        "suggested-authors/",
        SuggestedAuthorsView.as_view(),
        name="suggested-authors"
    ),

    # Personalized feed
    path(
        "feed/",
        PersonalizedFeedView.as_view(),
        name="personalized-feed"
    ),

]