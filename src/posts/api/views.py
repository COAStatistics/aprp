from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.template.loader import render_to_string
from posts import models
from . import serializers
from . import paginations


class PostListAllAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListAllSerializer
    queryset = models.Post.objects.all()
    # pagination_class = paginations.PostPageNumberPagination


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.PostCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        post = models.Post.objects.get(id=serializer.data['id'])

        html = render_to_string('post.html', {'post': post}, request=request)

        return Response(html, status=status.HTTP_201_CREATED, headers=headers)
