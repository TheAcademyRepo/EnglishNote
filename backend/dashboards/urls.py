from django.urls import path

from .views import (
    DashboardOverviewView,
    MyDashboardContentView,
    ContentReviewQueueView,
    DashboardUserListView,
    PlatformStatisticsView,
)


urlpatterns = [

    path(
        "overview/",
        DashboardOverviewView.as_view(),
        name="dashboard-overview"
    ),

    path(
        "my-content/",
        MyDashboardContentView.as_view(),
        name="dashboard-my-content"
    ),

    path(
        "review-queue/",
        ContentReviewQueueView.as_view(),
        name="dashboard-review-queue"
    ),

    path(
        "users/",
        DashboardUserListView.as_view(),
        name="dashboard-users"
    ),

    path(
        "statistics/",
        PlatformStatisticsView.as_view(),
        name="dashboard-statistics"
    ),

]