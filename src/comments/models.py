from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import(
    Manager,
    Model,
    ForeignKey,
    PositiveIntegerField,
    TextField,
    FileField,
    DateTimeField,
    CASCADE,
    Q
)
from django.utils.translation import ugettext_lazy as _
from .utils import upload_location

COMMENT_CONTENT_TYPE_CHOICES = (Q(app_label='posts', model='post'))


class CommentManager(Manager):
    def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs

    def filter_by_instance(self, instance):
        object_id = instance.id
        qs = super(CommentManager, self).filter(object_id=object_id).filter(parent=None)
        return qs

    def create_by_content_type(self, model_type, object_id, content, user, parent_obj=None):
        model_qs = ContentType.objects.filter(model=model_type)
        if model_qs.exists():
            content_type = model_qs.first().model_class()
            obj_qs = content_type.objects.filter(id=object_id)
            if obj_qs.exists() and obj_qs.count() == 1:
                instance = self.model()
                instance.content = content
                instance.user = user
                instance.content_type = model_qs.first()
                instance.object_id = obj_qs.first().id
                if parent_obj:
                    instance.parent = parent_obj
                instance.save()
                return instance
        return None


class Comment(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, default=1)
    content_type = ForeignKey(ContentType,
                              limit_choices_to=COMMENT_CONTENT_TYPE_CHOICES,
                              on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = ForeignKey('self', null=True, blank=True, verbose_name=_('Parent'))
    file = FileField(upload_to=upload_location, null=True, blank=True, verbose_name=_('File'))
    content = TextField(verbose_name=_('Content'))
    timestamp = DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))

    objects = CommentManager()

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-timestamp']

    def __unicode__(self):
        return str(self.user.username)

    def __str__(self):
        return str(self.user.username)

    def get_absolute_url(self):
        return reverse('comments:thread', kwargs={'id': self.id})

    def get_delete_url(self):
        return reverse('comments:delete', kwargs={'id': self.id})

    def children(self):  # replies
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        return self.parent is None




        
            
            


