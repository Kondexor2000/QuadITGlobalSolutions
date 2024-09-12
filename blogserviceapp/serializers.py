from rest_framework import serializers
from .models import Post, Comment, Category, Message, BlockedUser, User

class PostSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=False
    )

    class Meta:
        model = Post
        fields = ['title', 'description', 'category_id', 'image']


class BlockedUserSerializer(serializers.ModelSerializer):
    blocked_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(), 
        many=True 
    )

    class Meta:
        model = BlockedUser
        fields = ['blocked_users']

    def __init__(self, *args, **kwargs):
        request = kwargs.get('context', {}).get('request')
        if request:
            query = request.GET.get('q')
            if query:
                self.fields['blocked_users'].queryset = User.objects.filter(username__icontains=query)
        super().__init__(*args, **kwargs)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['description']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['description']