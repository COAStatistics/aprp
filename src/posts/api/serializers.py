from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField
    )


from accounts.api.serializers import UserDetailSerializer
from posts.models import Post


class PostListSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Post
        fields = [
            'user',
            'title',
            'content',
            'publish',
]