from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from publishing.models import ContentItem
from engagement.models import Like, Comment

from .models import Notification


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):

    if not created:
        return

    content = instance.content
    actor = instance.user
    recipient = content.author

    if actor_id := actor.pk:
        if recipient.pk != actor_id:
            Notification.objects.create(
                recipient=recipient,
                actor=actor,
                notification_type=Notification.NotificationType.LIKE,
                content=content,
                message=f"{actor.username} liked your content."
            )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):

    if not created:
        return

    content = instance.content
    actor = instance.user

    # Notify the content author.
    if content.author_id != actor.pk:
        Notification.objects.create(
            recipient=content.author,
            actor=actor,
            notification_type=Notification.NotificationType.COMMENT,
            content=content,
            comment=instance,
            message=f"{actor.username} commented on your content."
        )

    # If this is a reply, notify the parent comment's author.
    if instance.parent_id:
        parent = instance.parent

        if parent.user_id and parent.user_id != actor.pk:
            Notification.objects.create(
                recipient=parent.user,
                actor=actor,
                notification_type=Notification.NotificationType.REPLY,
                content=content,
                comment=instance,
                message=f"{actor.username} replied to your comment."
            )


@receiver(pre_save, sender=ContentItem)
def remember_previous_content_status(sender, instance, **kwargs):

    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        ContentItem.objects
        .filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )


@receiver(post_save, sender=ContentItem)
def notify_author_when_published(sender, instance, created, **kwargs):

    previous_status = getattr(instance, "_previous_status", None)

    was_published = previous_status == ContentItem.Status.PUBLISHED
    is_published = instance.status == ContentItem.Status.PUBLISHED

    if is_published and not was_published:

        # Do not notify the author about their own publication.
        # This signal is reserved for future workflow extensions.
        return