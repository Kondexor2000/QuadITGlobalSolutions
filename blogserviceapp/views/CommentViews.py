from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework import generics, permissions
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Post, Comment, BlockedUser
from blogserviceapp.serializers import CommentSerializer

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        serializer.save(user_id=self.request.user, post_id=post)

class UpdateCommentView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        return Comment.objects.filter(user_id=self.request.user, post_id=post)

class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        return Comment.objects.filter(user_id=self.request.user, post_id=post)
    
def comments_by_post_view(request, category_pk, post_pk):
    template_name = 'read_comments.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
    post = get_object_or_404(Post, pk=post_pk, category_id=category_pk)
    comments = Comment.objects.filter(post_id=post).exclude(user_id__in=blocked_users)
    
    return render(request, template_name, {'comments': comments})