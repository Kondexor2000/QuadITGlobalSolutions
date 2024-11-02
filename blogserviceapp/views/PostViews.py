from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from rest_framework import generics, permissions
from blogserviceapp.models import Post, Category, BlockedUser, User
from blogserviceapp.serializers import PostSerializer
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

class AddPostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        logger.info(f"User {self.request.user} is creating a post.")
        try:
            serializer.save(user_id=self.request.user)
            logger.info(f"Post created successfully by user {self.request.user}.")
        except Exception as e:
            logger.error(f"Error while creating post by user {self.request.user}: {e}")
            raise

class UpdatePostView(generics.UpdateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info(f"User {self.request.user} is accessing posts for updating.")
        return Post.objects.filter(user_id=self.request.user)

class DeletePostView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info(f"User {self.request.user} is accessing posts for deletion.")
        return Post.objects.filter(user_id=self.request.user)
    
def posts_by_category_view(request, category_pk):
    logger.info(f"User {request.user} requested posts in category {category_pk}.")
    template_name = 'read_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    try:
        blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
        category = get_object_or_404(Category, pk=category_pk)
        posts = Post.objects.filter(category_id=category).exclude(user_id__in=blocked_users).values("image", "title", "description")
        logger.info(f"Posts for category {category_pk} retrieved successfully for user {request.user}.")
    except Exception as e:
        logger.error(f"Error retrieving posts for category {category_pk} by user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving posts.", status=500)
    
    return render(request, template_name, {'posts': posts})

def posts_readed_view(request):
    logger.info(f"User {request.user} requested all readable posts.")
    template_name = 'read_all_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    try:
        blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
        posts = Post.objects.exclude(user_id__in=blocked_users)
        logger.info(f"All posts retrieved successfully for user {request.user}.")
    except Exception as e:
        logger.error(f"Error retrieving all posts for user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving posts.", status=500)

    return render(request, template_name, {'posts': posts})

def posts_by_request_user(request):
    logger.info(f"User {request.user} requested their own posts.")
    template_name = 'read_request_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    try:
        posts = Post.objects.filter(user_id=request.user)
        logger.info(f"Posts by user {request.user} retrieved successfully.")
    except Exception as e:
        logger.error(f"Error retrieving posts by user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving your posts.", status=500)

    return render(request, template_name, {'posts': posts})

def posts_by_searched_user(request, user_pk):
    logger.info(f"User {request.user} requested posts by searched user {user_pk}.")
    template_name = 'read_searched_posts.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.", status=404)

    try:
        blocked_users = BlockedUser.objects.filter(id_user=request.user).values_list('blocked_user', flat=True)
        user = get_object_or_404(User, pk=user_pk)

        if user.pk not in blocked_users:
            posts = Post.objects.filter(user_id=user)
            logger.info(f"Posts by user {user_pk} retrieved successfully for user {request.user}.")
        else:
            posts = []
            logger.warning(f"User {request.user} is blocked from viewing posts by user {user_pk}.")
    except Exception as e:
        logger.error(f"Error retrieving posts by user {user_pk} for user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving posts.", status=500)

    return render(request, template_name, {'posts': posts})