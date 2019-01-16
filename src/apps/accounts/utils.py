import random
import string

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

KEY_MIN = getattr(settings, "KEY_MIN", 30)


def code_generator(size=KEY_MIN,
                   chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def upload_location(instance, filename):
    model = instance.__class__
    last_obj = model.objects.order_by("id").last()

    if last_obj:
        new_id = last_obj.id + 1
    else:
        new_id = 1

    return "profile/%s/%s" % (new_id, filename)


def send_email(url, user, input_content):
    context = {
        'user': user.first_name,
        'url': url,
        'login_url': Site.objects.get_current().domain + '/accounts/login/',
    }
    context.update(input_content)
    html_content = render_to_string('mail_content.html', context)
    content = strip_tags(html_content)
    mail = EmailMultiAlternatives(input_content["mail_title"], content, settings.EMAIL_HOST_USER, [user.email])
    mail.attach_alternative(html_content, "text/html")
    mail.send(fail_silently=False)
