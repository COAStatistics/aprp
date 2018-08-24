from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from .forms import CommentForm
from .models import Comment


def comment_create(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
    else:
        form = CommentForm()
    return save_comment_form(request, form, 'partial_comment_create.html')


def comment_update(request, pk):
    comment = Comment.objects.filter(id=pk).first()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
    else:
        form = CommentForm(instance=comment)
    return save_comment_form(request, form, 'partial_comment_update.html')


def save_comment_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():

            comment = form.save(commit=False)
            comment.content_type = ContentType.objects.get(app_label="posts", model="post")
            comment.user = request.user
            comment.save()

            post = comment.content_object

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


def comment_delete(request, pk):
    comment = Comment.objects.filter(id=pk).first()
    data = dict()
    if request.method == 'POST' and comment.user == request.user:

        post = comment.content_object
        comment.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        data['html_post'] = render_to_string('partial_post.html', {
            'post': post,
            'user': request.user
        })

    else:
        context = {'comment': comment}
        data['html_form'] = render_to_string(
            'partial_comment_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

