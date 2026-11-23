from django.urls import path

from .views import (
    PostListCreateView,
    PostDetail,
    CategoryList,
    CommentListCreate,
    PostLikeView,
    SubjectList,
    TopicListView,
    NoteList,
    DailypostList,
    DailypostDetail,
)

urlpatterns = [
    path("categories/", CategoryList.as_view(), name="category-list"),
    path("posts/", PostListCreateView.as_view(), name="post-list"),
    path("topics/", TopicListView.as_view(), name="topics-list"),
    path("subjects/", SubjectList.as_view(), name="subject-list"),
    path("note/", NoteList.as_view(), name="note-list"),
    path("dailypost/", DailypostList.as_view(), name="dailypost-list"),
    path("posts/<slug:slug>/", PostDetail.as_view(), name="post-detail"),
    path("dailypost/<slug:slug>/", DailypostDetail.as_view(), name="dailypost-detail"),
    path("posts/<slug:slug>/comments/", CommentListCreate.as_view(), name="post-comments"),
    path("posts/<slug:slug>/like/", PostLikeView.as_view(), name="post-like"),
]
