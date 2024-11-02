from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from rest_framework import generics, permissions
from django.template import TemplateDoesNotExist
from blogserviceapp.models import BlockedUser, User
from blogserviceapp.serializers import BlockedUserSerializer
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

class AddBlockedUserView(generics.CreateAPIView):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        logger.info(f"User {self.request.user} is attempting to block user {user}.")
        serializer.save(id_user=self.request.user, blocked_user=user)
        logger.info(f"User {user} was successfully blocked by {self.request.user}.")

class UpdateBlockedUserView(generics.UpdateAPIView):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        logger.info(f"Fetching blocked user entry for update: {self.request.user} blocking {user}.")
        return BlockedUser.objects.filter(id_user=self.request.user, blocked_user=user)

class DeleteBlockedUserView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        logger.info(f"Fetching blocked user entry for deletion: {self.request.user} blocking {user}.")
        return BlockedUser.objects.filter(id_user=self.request.user, blocked_user=user)

def blocked_users_view(request):
    template_name = 'blocked_users.html'
    if not check_template_exists(template_name, request):
        logger.warning(f"Template '{template_name}' not found for user {request.user}.")
        return HttpResponseNotFound("Template not found.")
    
    blocked_users = BlockedUser.objects.filter(blocked_user=request.user)
    logger.info(f"User {request.user} accessed blocked users view with {blocked_users.count()} entries.")
    
    return render(request, template_name, {'blocked_users': blocked_users})