from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.http import JsonResponse
from posts import models
from posts import forms
from . import serializers
#from . import paginations


class PostListAllAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListAllSerializer
    queryset = models.Post.objects.all()
    permission_class = [IsAuthenticated]
    # pagination_class = paginations.PostPageNumberPagination


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.PostCreateSerializer
    permission_class = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        user = request.user.id
        try:
            data = {
                'user': user,
                'title':  request.data['title'],
                'content': request.data['content'],
                'file': request.data['file'],
            }
        except:
            data = {
                'user': user,
                'title':  request.data['title'],
                'content': request.data['content'],
            }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        post = models.Post.objects.get(id=serializer.data['id'])

        html = render_to_string('post.html', {'post': post}, request=request)

        return Response(html, status=status.HTTP_201_CREATED, headers=headers)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostRetrieveUpdateDestroySerializer
    permission_class = [IsAuthenticated]

    def get_object(self):
        instance = models.Post.objects.get(id=self.kwargs.get('pk'))
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return serializer.data

    def get(self, request, *args, **kwargs):
        data = self.retrieve(request, *args, **kwargs)
        form = forms.PostForm(data)
        html = render_to_string('form_edit.html', {'form': form, 'file': data['file'], 'id': data['id']}, request=request)
        data['html'] = html
        return JsonResponse(data, safe=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return serializer.data

    def patch(self, request, *args, **kwargs):
        data = self.partial_update(request, *args, **kwargs)
        html = render_to_string('post_edit.html', {'data': data}, request=request)
        return JsonResponse(html, safe=False)
