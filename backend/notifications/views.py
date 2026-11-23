from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Notification
from .serializers import NotificationSerializer


class NotificationPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50


class NotificationListView(generics.ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):

        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            "actor",
            "content",
            "comment"
        )

        unread = self.request.query_params.get("unread")

        if unread == "true":
            queryset = queryset.filter(is_read=False)

        elif unread == "false":
            queryset = queryset.filter(is_read=True)

        return queryset


class UnreadNotificationCountView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({
            "unread_count": count
        })


class MarkNotificationReadView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):

        notification = generics.get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )

        if not notification.is_read:

            notification.is_read = True

            notification.save(
                update_fields=["is_read"]
            )

        return Response({
            "message": "Notification marked as read."
        })


class MarkAllNotificationsReadView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": "Notifications marked as read.",
            "updated_count": updated
        })


class DeleteNotificationView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):

        notification = generics.get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )

        notification.delete()

        return Response(
            {"message": "Notification deleted."},
            status=status.HTTP_200_OK
        )