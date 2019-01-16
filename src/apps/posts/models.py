from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import (
    Manager,
    Model,
    ForeignKey,
    CharField,
    FileField,
    IntegerField,
    DateField,
    DateTimeField
)
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.safestring import mark_safe
from markdown_deux import markdown
from .utils import get_read_time, upload_location
from django.utils.translation import ugettext_lazy as _
from apps.comments.models import Comment

from ckeditor.fields import RichTextField


class PostManager(Manager):
    def active(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return super(PostManager, self).filter(publish__lte=timezone.now())


class Post(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, default=1, verbose_name=_('User'))
    title = CharField(max_length=120, verbose_name=_('Title'))
    file = FileField(upload_to=upload_location, null=True, blank=True, verbose_name=_('File'))
    content = RichTextField(verbose_name=_('Content'))
    publish = DateField(auto_now=False, default=timezone.now, verbose_name=_('Publish'))
    read_time = IntegerField(default=0, verbose_name=_('Read Time'))  # TimeField(null=True, blank=True) #assume minutes
    updated = DateTimeField(auto_now=True, verbose_name=_('Updated'))
    timestamp = DateTimeField(auto_now=False, auto_now_add=True, verbose_name=_('Timestamp'))

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ["-timestamp", "-updated"]

    objects = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"id": self.id})

    def get_api_url(self):
        return reverse("posts-api:detail", kwargs={"id": self.id})

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def pre_save_post_receiver(sender, instance, *args, **kwargs):

    if instance.content:
        html_string = instance.get_markdown()
        read_time_var = get_read_time(html_string)
        instance.read_time = read_time_var


pre_save.connect(pre_save_post_receiver, sender=Post)
