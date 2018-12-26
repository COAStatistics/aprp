from django.conf import settings
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
from django.db.models import (
    QuerySet,
    CASCADE,
    OneToOneField,
    CharField,
    SET_NULL,
    ForeignKey,
    Model,
    BooleanField,
    ImageField,
    EmailField,
)
from .utils import code_generator, upload_location, send_email


class GroupInformationQuerySet(QuerySet):
    def end_groups(self):
        ids = []
        try:
            for group in self.all():
                if not group.has_child:
                    ids.append(group.id)
            return self.filter(id__in=ids)
        except:
            pass


class GroupInformation(Model):
    name = CharField(max_length=120, verbose_name=_('Name'))
    group = OneToOneField(Group, on_delete=CASCADE, related_name='info', verbose_name=_('Group'))
    email_dns = CharField(max_length=255, validators=[URLValidator], verbose_name=_('Email Dns'))
    parent = ForeignKey('self', null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Parent'))

    objects = GroupInformationQuerySet.as_manager()

    class Meta:
        verbose_name = _('Group Information')
        verbose_name_plural = _('Group Informations')

    def __str__(self):
        return str(self.group.name)

    def __unicode__(self):
        return str(self.group.name)

    def parents(self):
        parents = [self]
        lock = False
        obj = self
        while not lock:
            parent = obj.parent
            if parent:
                parents.append(parent)
                obj = parent
            else:
                lock = True
        return parents

    @property
    def has_child(self):
        return GroupInformation.objects.filter(parent=self).count() > 0


class UserInformation(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL,
                         on_delete=CASCADE,
                         related_name='info',
                         verbose_name=_('User'))
    event_editor = BooleanField(default=False, verbose_name=_('Event Editor'))
    watchlist_viewer = BooleanField(default=False, verbose_name=_('Watchlist Viewer'))
    menu_viewer = BooleanField(default=False, verbose_name=_('Menu Item Viewer'))
    reporter = BooleanField(default=False, verbose_name=_('Reporter'))
    alert_viewer = BooleanField(default=True, verbose_name=_('Alert Viewer'))
    monitor_info_viewer = BooleanField(default=True, verbose_name=_('Monitor Info Viewer'))
    profile = ImageField(upload_to=upload_location, null=True, blank=True, verbose_name=_('Profile'))

    class Meta:
        verbose_name = _('User Information')
        verbose_name_plural = _('User Informations')

    def __str__(self):
        return str(self.full_name)

    def __unicode__(self):
        return str(self.full_name)

    @property
    def full_name(self):
        name = str(self.user.last_name) + str(self.user.first_name)
        if name == '':
            name = self.user.username
        return name


class AbstractProfile(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    key = CharField(max_length=120, verbose_name=_('Activate Key'))
    expired = BooleanField(default=False, verbose_name=_('Expired'))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _('Abstract Profile')
        verbose_name_plural = _('Abstract Profiles')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = code_generator()
        super(AbstractProfile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user.username)

    def __unicode__(self):
        return str(self.user.username)


# User Create Event: 1. Set is_active False 2. Create UserInformation 3. Create ActivationProfile
def post_save_user_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            UserInformation.objects.create(user=instance)
            if not instance.is_superuser:
                instance.is_active = False
                instance.save()
                ActivationProfile.objects.create(user=instance)
        except:
            pass


post_save.connect(post_save_user_model_receiver, sender=settings.AUTH_USER_MODEL)


class ActivationProfile(AbstractProfile):
    class Meta:
        verbose_name = _('Activation Profile')
        verbose_name_plural = _('Activation Profiles')

    def get_activate_url(self):
        return Site.objects.get_current().domain + reverse('accounts:activate', kwargs={'key': self.key})


# ActivationProfile Create Event: Send Email
def post_save_activation_receiver(sender, instance, created, *args, **kwargs):
    if created:
        content = {
            'btn_text': _('Activate My Account'),
            'mail_title': '{} - {}'.format(_('Agriculture Products Price Report Platform'), _('Account Activation')),
            'line_1': _('Please activate your account by clicking the link below'),
            'line_2': _('Thank you for your registration')
        }
        activate_url = instance.get_activate_url()
        send_email(activate_url, instance.user, content)


post_save.connect(post_save_activation_receiver, sender=ActivationProfile)


class ResetPasswordProfile(AbstractProfile):
    class Meta:
        verbose_name = _('Reset Password Profile')
        verbose_name_plural = _('Reset Password Profiles')

    def get_absolute_url(self):
        return Site.objects.get_current().domain + reverse('accounts:reset_password', kwargs={'key': self.key})


# ResetPasswordProfile Create Event: Send Email
def post_save_reset_password_receiver(sender, instance, created, *args, **kwargs):
    if created:
        content = {
            'btn_text': _('Reset Password'),
            'mail_title': '{} - {}'.format(_('Agriculture Products Price Report Platform'), _('Reset Password')),
            'line_1': _('Please click the following button to reset your password')
        }
        reset_url = instance.get_absolute_url()
        send_email(reset_url, instance.user, content)


post_save.connect(post_save_reset_password_receiver, sender=ResetPasswordProfile)


class ResetEmailProfile(AbstractProfile):
    new_email = EmailField(verbose_name=_('Reset Email'))

    class Meta:
        verbose_name = _('Reset Email Profile')
        verbose_name_plural = _('Reset Email Profiles')

    def get_absolute_url(self):
        return Site.objects.get_current().domain + reverse('accounts:reset_email', kwargs={'key': self.key})


# ResetEmailProfile Create Event: Send Email
def post_save_reset_email_receiver(sender, instance, created, *args, **kwargs):
    if created:
        content = {
            'btn_text': _('Reset Email'),
            'mail_title': '{} - {}'.format(_('Agriculture Products Price Report Platform'), _('Reset Email')),
            'line_1': _('Please click the following button to reset your email')
        }
        reset_url = instance.get_absolute_url()
        send_email(reset_url, instance.user, content)


post_save.connect(post_save_reset_email_receiver, sender=ResetEmailProfile)
