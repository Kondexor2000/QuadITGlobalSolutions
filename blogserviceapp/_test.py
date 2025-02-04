import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Post, Comment, Message, BlockedUser

@pytest.fixture
def category(db):
    return Category.objects.create(name='Test Category')

@pytest.fixture
def post(user, category):
    return Post.objects.create(
        title='Test Post',
        description='Test Description',
        category_id=category,
        user_id=user
    )

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.fixture
def logged_in_client(client, user):
    client.login(username='testuser', password='testpassword')
    return client

@pytest.mark.django_db
def test_signup_view(client):
    response = client.get(reverse('signup'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_edit_profile_view(logged_in_client):
    response = logged_in_client.get(reverse('edit_profile'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_account_view(logged_in_client):
    response = logged_in_client.get(reverse('delete_account'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_view(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_logout_view(logged_in_client):
    response = logged_in_client.get(reverse('logout'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_explore_post_categories_view(logged_in_client):
    response = logged_in_client.get(reverse('categories'))
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_explore_posts_view(logged_in_client):
    response = logged_in_client.get(reverse('index'))
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_explore_blocked_users_view(logged_in_client):
    response = logged_in_client.get(reverse('read_blocked_user'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_request_users_view(logged_in_client):
    response = logged_in_client.get(reverse('request_user'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_post_by_category_view(logged_in_client, category):
    response = logged_in_client.get(reverse('posts_by_category', args=[category.pk]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_message_view(logged_in_client, user):
    response = logged_in_client.get(reverse('read_message', args=[user.pk]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_explore_comments_by_post_view(logged_in_client, post, category):
    response = logged_in_client.get(reverse('comments_by_post', args=[category.pk, post.pk]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_category_creation():
    category = Category.objects.create(name='Test Category', description='Test Description')
    assert category.name == 'Test Category'
    assert category.description == 'Test Description'

@pytest.mark.django_db
def test_message_creation(user):
    message = Message.objects.create(
        author=user,
        description='Test Message'
    )
    message.sender.add(user)
    assert message.author == user
    assert message.description == 'Test Message'
    assert message.sender.count() == 1
    assert user in message.sender.all()

@pytest.mark.django_db
def test_blocked_user_creation(user):
    other_user = User.objects.create_user(username='blockeduser', password='testpassword')
    blocked_user = BlockedUser.objects.create(
        blocked_user=other_user,
        id_user=user
    )
    assert blocked_user.blocked_user == other_user
    assert blocked_user.id_user == user