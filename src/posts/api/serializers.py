from rest_framework import serializers
from accounts.api.serializers import UserUsernameSerializer
from comments.api.serializers import CommentListAllSerializer

from posts import models


class PostListAllSerializer(serializers.ModelSerializer):
    user = UserUsernameSerializer()
    comments = CommentListAllSerializer(many=True)

    class Meta:
        model = models.Post
        fields = [
            'id',
            'user',
            'title',
            'content',
            'file',
            'comments',
            'timestamp',
            'updated',
        ]


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Post
        fields = [
            'id',
            'user',
            'title',
            'content',
            'file',
        ]
