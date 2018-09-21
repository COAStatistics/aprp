from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

from comments.models import Comment
from . import models
from . import forms

import json
import requests


def post_socialwall(request):

    post_list = models.Post.objects.all()
    form = forms.PostForm()

    return render(request, 'socialwall.html', locals())


def post_new_form(request):

    form = forms.PostForm()
    html = render_to_string('form.html', {'form': form}, request=request)

    return JsonResponse(html, safe=False)


def post_search(request):

    key = request.GET.get('key')
    q = request.GET.get('q')
    posts = models.Post.objects.all()
    # search_name = "search_{}".format(key)

    if key == "Everything":
        comments = Comment.objects.all()
        comments = comments.filter(
            Q(content__icontains=q)
        )
        post_list = []
        for i in comments:
            try:
                if i.content_object.id not in post_list:
                    post_list.append(i.content_object.id)
            except:
                pass
        query = posts.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(user__username__icontains=q) |
            Q(id__in=post_list)
        )
    elif key == "Title":
        query = posts.filter(
            Q(title__icontains=q)
        )
    elif key == "Author":
        query = posts.filter(
            Q(user__username__icontains=q)
        )
    elif key == "Content":
        query = posts.filter(
            Q(content__icontains=q)
        )
    elif key == "Comment":
        comments = Comment.objects.all()
        comments = comments.filter(
            Q(content__icontains=q)
        )
        post_list = []
        for i in comments:
            try:
                if i.content_object.id not in post_list:
                    post_list.append(i.content_object.id)
            except:
                pass
        query = models.Post.objects.filter(id__in=post_list)

    if query.count() == 0:
        html = render_to_string('socialwall404.html', {'q': q})
    else:
        html = render_to_string('post_area.html', {'post_list': query}, request=request)

    return HttpResponse(html)
