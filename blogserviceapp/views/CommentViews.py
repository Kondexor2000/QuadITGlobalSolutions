import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework import generics, permissions
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Post, Comment, BlockedUser
from blogserviceapp.serializers import CommentSerializer

# Konfiguracja loggera
logger = logging.getLogger(__name__)

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        logger.info(f"Template '{template_name}' found.")
        return True
    except TemplateDoesNotExist:
        logger.error(f"Template '{template_name}' does not exist.")
        return False

class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_pk = self.kwargs.get('post_pk')
        try:
            post = get_object_or_404(Post, pk=post_pk)
            serializer.save(user_id=self.request.user, post_id=post)
            logger.info(f"User {self.request.user} created a comment on post {post_pk}.")
        except Exception as e:
            logger.error(f"Error creating comment for post {post_pk} by user {self.request.user}: {e}")
            raise

class UpdateCommentView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        try:
            post = get_object_or_404(Post, pk=post_pk)
            logger.info(f"User {self.request.user} is updating a comment for post {post_pk}.")
            return Comment.objects.filter(user_id=self.request.user, post_id=post)
        except Exception as e:
            logger.error(f"Error fetching comments for updating for post {post_pk} by user {self.request.user}: {e}")
            raise

class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        try:
            post = get_object_or_404(Post, pk=post_pk)
            logger.info(f"User {self.request.user} is deleting a comment for post {post_pk}.")
            return Comment.objects.filter(user_id=self.request.user, post_id=post)
        except Exception as e:
            logger.error(f"Error fetching comments for deletion for post {post_pk} by user {self.request.user}: {e}")
            raise
    
def comments_by_post_view(request, category_pk, post_pk):
    template_name = 'read_comments.html'
    if not check_template_exists(template_name, request):
        logger.warning(f"User {request.user} requested a non-existent template '{template_name}'.")
        return HttpResponse("Template not found.", status=404)

    try:
        blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
        post = get_object_or_404(Post, pk=post_pk, category_id=category_pk)
        comments = Comment.objects.filter(post_id=post).exclude(user_id__in=blocked_users)
        logger.info(f"Comments for post {post_pk} retrieved by user {request.user}.")
        return render(request, template_name, {'comments': comments})
    except Exception as e:
        logger.error(f"Error retrieving comments for post {post_pk} by user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving comments.", status=500)