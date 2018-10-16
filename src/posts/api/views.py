from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
from posts import models
from posts import forms
from comments.models import Comment
from dashboard import settings
from . import serializers
from . import paginations
import os


class PostListAllAPIView(generics.ListAPIView):
    serializer_class = serializers.PostListAllSerializer
    queryset = models.Post.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.PostPageNumberPagination

    def initial(self, request, *args, **kwargs):
        super(PostListAllAPIView, self).initial(request, *args, **kwargs)

        # setting
        self.page = request.query_params.get('page', None)
        self.keyword = request.query_params.get('keyword', None)
        self.value = request.query_params.get('value', None)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if self.keyword == "All":
            comments = Comment.objects.all()
            comments = comments.filter(
                Q(content__icontains=self.value)
            )
            post_list = []
            for i in comments:
                try:
                    if i.content_object.id not in post_list:
                        post_list.append(i.content_object.id)
                except:
                    pass
            temp1 = queryset.filter(
                Q(title__icontains=self.value) |
                Q(content__icontains=self.value) |
                Q(id__in=post_list)
            )
            temp2 = queryset.filter(
                Q(user__username__icontains=self.value) |
                Q(user__last_name__icontains=self.value) |
                Q(user__first_name__icontains=self.value)
            )
            if temp2.count() == 0:
                last_name = self.value[0]
                first_name = self.value[1:]
                temp2 = queryset.filter(user__last_name__icontains=last_name).filter(user__first_name__icontains=first_name)
            id_list = []
            for i in temp1:
                if i.id not in id_list:
                    id_list.append(i.id)
            for i in temp2:
                if i.id not in id_list:
                    id_list.append(i.id)
            queryset = queryset.filter(id__in=id_list)
        elif self.keyword == "Title":
            queryset = queryset.filter(
                Q(title__icontains=self.value)
            )
        elif self.keyword == "Author":
            temp = queryset.filter(
                Q(user__username__icontains=self.value) |
                Q(user__last_name__icontains=self.value) |
                Q(user__first_name__icontains=self.value)
            )
            if temp.count() == 0:
                last_name = self.value[0]
                first_name = self.value[1:]
                temp = queryset.filter(user__last_name__icontains=last_name).filter(user__first_name__icontains=first_name)
            queryset = temp
        elif self.keyword == "Content":
            queryset = queryset.filter(
                Q(content__icontains=self.value)
            )
        elif self.keyword == "Comment":
            comments = Comment.objects.all()
            comments = comments.filter(
                Q(content__icontains=self.value)
            )
            post_list = []
            for i in comments:
                try:
                    if i.content_object.id not in post_list:
                        post_list.append(i.content_object.id)
                except:
                    pass
            queryset = queryset.filter(id__in=post_list)
        else:
            queryset = queryset

        page = self.paginate_queryset(queryset.order_by('-timestamp'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            serializer = self.get_paginated_response(serializer.data)
            id_list = []
            for i in serializer.data['results']:
                id_list.append(i['id'])
        else:
            serializer = self.get_serializer(queryset, many=True)
            id_list = []
            for i in serializer.data:
                id_list.append(i['id'])
        post_list = queryset.filter(id__in=id_list)
        if post_list.count() == 0:
            html = render_to_string('socialwall404.html', {'q': self.value}, request=request)
        else:
            html = render_to_string('post_area.html', {'post_list': post_list}, request=request)
        context = {
            'api': serializer.data,
            'html': html,
        }
        return Response(context)


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.PostCreateSerializer
    permission_classes = [IsAuthenticated]

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

        context = {
            'api': serializer.data,
            'html': render_to_string('post.html', {'post': post}, request=request),
        }

        return Response(context, status=status.HTTP_201_CREATED, headers=headers)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.PostRetrieveUpdateDestroySerializer
    queryset = models.Post.objects.all()
    permission_classes = [IsAuthenticated]

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
        context = {
            'api': data,
            'html': render_to_string('form_edit.html', {'form': form, 'file': data['file'], 'id': data['id']}, request=request),
        }
        return Response(context)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            if request.data['file']:
                os.remove(instance.file.path)
        except:
            pass

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return serializer.data

    def patch(self, request, *args, **kwargs):
        data = self.partial_update(request, *args, **kwargs)
        obj = models.Post.objects.get(id=data['id'])
        context = {
            'api': data,
            'html': render_to_string('post_edit.html', {'data': obj}, request=request),
        }
        # return JsonResponse(html, safe=False)
        return Response(context)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            os.remove(instance.file.path)
            os.rmdir(os.path.join(settings.MEDIA_ROOT, "post/{}".format(instance.id)))
        except:
            pass
            
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
