from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Message, User, BlockedUser
from blogserviceapp.serializers import MessageSerializer
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        logger.info(f"Template '{template_name}' found for user {request.user}.")
        return True
    except TemplateDoesNotExist:
        logger.error(f"Template '{template_name}' does not exist for user {request.user}.")
        return False

class AddMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        logger.info(f"User {self.request.user} is attempting to send a message to user {user_pk}.")

        blocking_users = BlockedUser.objects.filter(id_user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(id_user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            logger.warning(f"User {self.request.user} is blocked from sending a message to user {user_pk}.")
            raise PermissionDenied("You cannot send a message to this user.")
        
        serializer.save(author=self.request.user, sender=user)
        logger.info(f"Message successfully sent from user {self.request.user} to user {user_pk}.")

class UpdateMessageView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        logger.info(f"User {self.request.user} is attempting to update a message with user {user_pk}.")

        blocking_users = BlockedUser.objects.filter(user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            logger.warning(f"User {self.request.user} is blocked from updating messages involving user {user_pk}.")
            return Message.objects.none()

        return Message.objects.filter(author=self.request.user, sender=user)

class DeleteMessageView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        logger.info(f"User {self.request.user} is attempting to delete messages with user {user_pk}.")

        blocking_users = BlockedUser.objects.filter(user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            logger.warning(f"User {self.request.user} is blocked from deleting messages involving user {user_pk}.")
            return Message.objects.none()

        return Message.objects.filter(author=self.request.user, sender=user)

def message_to_sender_view(request, user_pk):
    logger.info(f"User {request.user} is viewing messages with user {user_pk}.")
    template_name = 'read_messages.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)
    
    user = get_object_or_404(User, pk=user_pk)

    blocking_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user_id', flat=True)
    blocked_users = BlockedUser.objects.filter(blocked_user=user).values_list('id_user_id', flat=True)

    if user.pk in blocking_users or request.user.pk in blocked_users:
        logger.warning(f"User {request.user} is blocked from viewing messages with user {user_pk}.")
        return HttpResponseForbidden("You cannot view messages from this user.")
    
    try:
        messages = Message.objects.filter(
            (Q(author=request.user) & Q(sender=user)) |
            (Q(author=user) & Q(sender=request.user))
        ).order_by('send_data')
        logger.info(f"Messages retrieved successfully for user {request.user} with user {user_pk}.")
    except Exception as e:
        logger.error(f"Error while retrieving messages for user {request.user} with user {user_pk}: {e}")
        return HttpResponse("An error occurred while retrieving messages.", status=500)

    return render(request, template_name, {'messages': messages})