from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from .forms import PostForm
from .models import Post
from django.db.models import Q
from urllib.parse import urlencode


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
    else:
        form = PostForm()
    return save_post_form(request, form, 'partial_post_create.html')


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
    else:
        form = PostForm(instance=post)
    return save_post_form(request, form, 'partial_post_update.html')


def save_post_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():

            post = form.save(commit=False)
            post.user = request.user
            post.save()

            data['form_is_valid'] = True
            data['html_post'] = render_to_string('partial_post.html', {
                'post': post,
                'user': request.user
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    data = dict()
    if request.method == 'POST' and post.user == request.user:
        post.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        data['html_post'] = None
    else:
        context = {'post': post}
        data['html_form'] = render_to_string('partial_post_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)


def post_list(request):
    data = dict()
    default_count = 5
    start = request.GET.get('start')
    count = request.GET.get('count')
    query = request.GET.get('q')

    posts = Post.objects.all()
    if query:
        posts = posts.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(user__username__icontains=query)
                ).distinct()

    if start:
        start = int(start)
        posts = posts[start:]

    if count:
        count = int(count)
    else:
        count = default_count

    context = {'posts': posts[:count]}
    data['html_posts'] = render_to_string('partial_post_list.html',
                                          context,
                                          request=request,)

    data['drained'] = posts.count() <= int(start)+default_count
    url = reverse('posts:post_list')
    args = {
        "count": 5,
        "start": int(start)+5,
        "q": query
    }
    data['url'] = "{0}?{1}".format(url, urlencode(args))

    return JsonResponse(data)






