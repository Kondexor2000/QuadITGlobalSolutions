from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from rest_framework import generics, permissions
from blogserviceapp.models import Post, Category, BlockedUser, User
from blogserviceapp.serializers import PostSerializer

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

class AddPostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

class UpdatePostView(generics.UpdateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user_id=self.request.user)

class DeletePostView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user_id=self.request.user)
    
def posts_by_category_view(request, category_pk):
    template_name = 'read_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.")

    blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
    category = get_object_or_404(Category, pk=category_pk)
    posts = Post.objects.filter(category_id=category).exclude(user_id__in=blocked_users).values("image", "title", "description")
    
    return render(request, template_name, {'posts': posts})

def posts_readed_view(request):
    template_name = 'read_all_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.")
    
    blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
    posts = Post.objects.exclude(user_id__in=blocked_users)
    
    return render(request, template_name, {'posts': posts})

def posts_by_request_user(request):
    template_name = 'read_request_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.")

    posts = Post.objects.filter(user_id=request.user)
    
    return render(request, template_name, {'posts': posts})

def posts_by_searched_user(request, user_pk):
    template_name = 'read_searched_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.")
    
    blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
    user = get_object_or_404(User, pk=user_pk)

    if user.pk not in blocked_users:
        posts = Post.objects.filter(user_id=user)
    else:
        posts = []
    
    return render(request, template_name, {'posts': posts})