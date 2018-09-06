from rest_framework import generics

from posts import models
from . import serializers


class PostListAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListSerializer
    queryset = models.Post.objects.all()
