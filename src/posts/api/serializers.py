from rest_framework import serializers
from accounts.api.serializers import UserDetailSerializer

from posts import models


class PostListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Post
        fields = '__all__'
