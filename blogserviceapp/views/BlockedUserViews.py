from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework import generics, permissions
from django.template import TemplateDoesNotExist
from blogserviceapp.models import BlockedUser, User
from blogserviceapp.serializers import BlockedUserSerializer

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

class AddBlockedUserView(generics.CreateAPIView):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        serializer.save(id_user=self.request.user, blocked_user=user)

class UpdateBlockedUserView(generics.UpdateAPIView):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        return BlockedUser.objects.filter(id_user=self.request.user, blocked_user=user)

class DeleteBlockedUserView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        return BlockedUser.objects.filter(id_user=self.request.user, blocked_user=user)

def blocked_users_view(request):
    template_name = 'blocked_users.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    blocked_users = BlockedUser.objects.filter(blocked_user=request.user)
    
    return render(request, template_name, {'blocked_users': blocked_users})