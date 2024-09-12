from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Message, User, BlockedUser
from blogserviceapp.serializers import MessageSerializer
from django.db.models import Q

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

class AddMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        blocking_users = BlockedUser.objects.filter(id_user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(id_user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            raise PermissionDenied("You cannot send a message to this user.")
        
        serializer.save(author=self.request.user, sender=user)

class UpdateMessageView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        blocking_users = BlockedUser.objects.filter(user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            return Message.objects.none() 

        return Message.objects.filter(author=self.request.user, sender=user)

class DeleteMessageView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        blocking_users = BlockedUser.objects.filter(user=self.request.user).values_list('blocked_user', flat=True)
        blocked_users = BlockedUser.objects.filter(user=user).values_list('blocked_user', flat=True)

        if user.pk in blocking_users or self.request.user.pk in blocked_users:
            return Message.objects.none() 

        return Message.objects.filter(author=self.request.user, sender=user)

def message_to_sender_view(request, user_pk):
    template_name = 'read_messages.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)
    
    user = get_object_or_404(User, pk=user_pk)

    blocking_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user_id', flat=True)
    blocked_users = BlockedUser.objects.filter(blocked_user=user).values_list('id_user_id', flat=True)

    if user.pk in blocking_users or request.user.pk in blocked_users:
        return HttpResponseForbidden("You cannot view messages from this user.")
    
    messages = Message.objects.filter(
        (Q(author=request.user) & Q(sender=user)) |
        (Q(author=user) & Q(sender=request.user))
    ).order_by('send_data')

    return render(request, template_name, {'messages': messages})