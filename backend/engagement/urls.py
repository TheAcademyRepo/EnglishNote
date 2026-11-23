from django.urls import path

from .views import (
    LikeToggleView,
    BookmarkToggleView,
    MyBookmarksView,
    ShareContentView,
    CommentListCreateView,
    CommentReplyListView,
    CommentDetailView,
    CommentModerationView,
    CreateReportView,
    MyReportsView,
    ReportManagementView,
    ResolveReportView,
    ContentEngagementSummaryView,
)


urlpatterns = [

    # Likes
    path(
        "content/<uuid:pk>/like/",
        LikeToggleView.as_view(),
        name="content-like"
    ),

    # Bookmarks
    path(
        "content/<uuid:pk>/bookmark/",
        BookmarkToggleView.as_view(),
        name="content-bookmark"
    ),

    path(
        "bookmarks/",
        MyBookmarksView.as_view(),
        name="my-bookmarks"
    ),

    # Shares
    path(
        "content/<uuid:pk>/share/",
        ShareContentView.as_view(),
        name="content-share"
    ),

    # Comments
    path(
        "content/<uuid:pk>/comments/",
        CommentListCreateView.as_view(),
        name="content-comments"
    ),

    path(
        "comments/<uuid:comment_id>/replies/",
        CommentReplyListView.as_view(),
        name="comment-replies"
    ),

    path(
        "comments/<uuid:id>/",
        CommentDetailView.as_view(),
        name="comment-detail"
    ),

    path(
        "comments/<uuid:comment_id>/moderate/",
        CommentModerationView.as_view(),
        name="comment-moderate"
    ),

    # Reports
    path(
        "reports/create/",
        CreateReportView.as_view(),
        name="report-create"
    ),

    path(
        "reports/mine/",
        MyReportsView.as_view(),
        name="my-reports"
    ),

    path(
        "reports/manage/",
        ReportManagementView.as_view(),
        name="report-management"
    ),

    path(
        "reports/<uuid:report_id>/resolve/",
        ResolveReportView.as_view(),
        name="report-resolve"
    ),

    # Engagement summary
    path(
        "content/<uuid:pk>/summary/",
        ContentEngagementSummaryView.as_view(),
        name="engagement-summary"
    ),

]