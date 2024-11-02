"""
URL configuration for blogservice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from blogserviceapp.views.AccountViews import (
    SignUpView,
    EditProfileView,
    DeleteAccountView,
    CustomLoginView,
    CustomLogoutView,
)
from blogserviceapp.views.PostViews import (
    AddPostView,
    UpdatePostView,
    DeletePostView,
    posts_by_category_view,
    posts_readed_view,
    posts_by_request_user,
    posts_by_searched_user
)
from blogserviceapp.views.CommentViews import (
    AddCommentView,
    UpdateCommentView,
    DeleteCommentView,
    comments_by_post_view,
)
from blogserviceapp.views.MessageViews import (
    AddMessageView,
    UpdateMessageView,
    DeleteMessageView,
    message_to_sender_view
)
from blogserviceapp.views.BlockedUserViews import (
    AddBlockedUserView,
    UpdateBlockedUserView,
    DeleteBlockedUserView,
    blocked_users_view
)
from blogserviceapp.views.CategoryViews import (
    category_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', posts_readed_view, name='index'),
    path('posts_pk/<int:user_pk>', posts_by_searched_user, name='searched_user'),
    path('posts_request/', posts_by_request_user, name='request_user'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    path('add-post/', AddPostView.as_view(), name='add_post'),
    path('update-post/<int:pk>/', UpdatePostView.as_view(), name='update_post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete_post'),

    path('add-message/<int:user_pk>', AddMessageView.as_view(), name='add_message'),
    path('update-message/<int:user_pk>/', UpdateMessageView.as_view(), name='update_message'),
    path('delete-message/<int:user_pk>/', DeleteMessageView.as_view(), name='delete_message'),
    path('read-message/<int:user_pk>/', message_to_sender_view, name='read_message'),

    path('add-blocked-user/<int:user_pk>', AddBlockedUserView.as_view(), name='add_blocked_user'),
    path('update-blocked-user/<int:user_pk>', UpdateBlockedUserView.as_view(), name='update_blocked_user'),
    path('delete-blocked-user/<int:user_pk>', DeleteBlockedUserView.as_view(), name='delete_blocked_user'),
    path('read-blocked-user/', blocked_users_view, name='read_blocked_user'),

    path('categories/', category_view, name='categories'),
    path('categories/<int:category_pk>/posts/', posts_by_category_view, name='posts_by_category'),
    path('categories/<int:category_pk>/posts/<int:post_pk>/comments/', comments_by_post_view, name='comments_by_post'),
    path('categories/<int:category_pk>/posts/<int:post_pk>/add-comment/', AddCommentView.as_view(), name='add_comment'),
    path('categories/<int:category_pk>/posts/<int:post_pk>/update-comment/<int:pk>/', UpdateCommentView.as_view(), name='update_comment'),
    path('categories/<int:category_pk>/posts/<int:post_pk>/delete-comment/<int:pk>/', DeleteCommentView.as_view(), name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)