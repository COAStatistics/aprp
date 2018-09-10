from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from comments import models
from . import serializers


class CommentListAllAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CommentListAllSerializer
    queryset = models.Comment.objects.all()

    # def create(self, request, *args, **kwargs):
    #     user = request.user.id
    #     content_type = 52
    #     data = {
    #         'user': user,
    #         'content_type': content_type,
    #         'object_id': request.data['object_id'],
    #         'content': request.data['content'],
    #     }
    #     # return JsonResponse(data)
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #
    #     comment = models.Comment.objects.get(id=serializer.data['id'])
    #     html = render_to_string('socialwall/reply.html', {'data': comment}, request=request)
    #
    #     return Response(html, status=status.HTTP_201_CREATED, headers=headers)
