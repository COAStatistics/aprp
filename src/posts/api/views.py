from rest_framework import generics
from posts import models
from . import serializers


class PostListAllAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListAllSerializer
    queryset = models.Post.objects.all()


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.PostCreateSerializer
