from django.http import Http404
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .forms import (
    UserLoginForm,
    UserRegisterForm,
    ResendEmailForm,
    UserResetPasswordForm,
)
from .models import (
    ActivationProfile,
    GroupInformation,
    ResetPasswordProfile,
    ResetEmailProfile
)
import logging

User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)
    content = {
        'form': form
    }
    template = 'login.html'

    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        #紀錄帳號每次登入時間
        dns = user.email.split('@')[1]
        group_info = GroupInformation.objects.filter(email_dns=dns).first()
        db_logger = logging.getLogger('aprp')
        db_logger.info(f'{user} {user.info} {group_info}', extra={'type_code': 'login'})
        # remember me
        if not form.cleaned_data.get('remember'):
            request.session.set_expiry(0)

        request.session['mail_sent'] = False
        return redirect(settings.LOGIN_REDIRECT_URL)

    if form.errors:
        is_active = form.cleaned_data.get('is_active')
        if is_active is False:
            content['resend_email'] = True

    return render(request, template, content)


def register_view(request):
    form = UserRegisterForm(request.POST or None)
    template = 'register.html'
    context = {
        "form": form
    }
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        # Assign user to groups
        dns = user.email.split('@')[1]
        group_info = GroupInformation.objects.filter(email_dns=dns).first()
        if group_info:
            for obj in group_info.parents():
                obj.group.user_set.add(user)
        messages.add_message(request, messages.INFO,
                             _('Successfully registered! Please check your email to activate your account'))
        return redirect('accounts:login')

    return render(request, template, context)


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def forgot_password_view(request):
    form = ResendEmailForm(request.POST or None)
    content = {
        "form": form,
        "title": _('Forgot Password')
    }
    template = 'resend-email.html'

    if form.is_valid():
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')

        if email:
            user = User.objects.get(email=email)
        if username:
            user = User.objects.get(username=username)

        ResetPasswordProfile.objects.create(user=user)

        content['mail_sent'] = True
        return render(request, template, content)

    return render(request, template, content)


def activation_resend_view(request):
    form = ResendEmailForm(request.POST or None)
    content = {
        "form": form,
        "title": _('Activate Account')
    }
    template = 'resend-email.html'

    if form.is_valid():
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')

        if email:
            user = User.objects.get(email=email)
        if username:
            user = User.objects.get(username=username)

        if user.is_active:
            form.add_error(field=None, error=_('Your account is already activated'))
        else:
            ActivationProfile.objects.create(user=user)
            content['mail_sent'] = True

        return render(request, template, content)

    return render(request, template, content)


def reset_password_view(request, key=None):
    template = 'reset-password.html'
    form = UserResetPasswordForm(request.POST or None)
    q = ResetPasswordProfile.objects.filter(key=key)
    context = {
        "form": form,
    }
    if q.exists():
        reset = q.first()
        if not reset.expired:
            context['valid_link'] = True

    if request.method == 'POST':
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = reset.user
            user.set_password(password)
            user.save()
            reset.expired = True
            reset.save()
            messages.add_message(request, messages.INFO,
                                 _('Your password has been reset'))
            return redirect('accounts:login')

    return render(request, template, context)


def user_activate(request, key=None, *args, **kwargs):
    q = ActivationProfile.objects.filter(key=key)

    if q.exists():
        activation = q.first()
        if not activation.expired:
            user = activation.user
            user.is_active = True
            user.save()
            activation.expired = True
            activation.save()
            messages.add_message(request, messages.INFO, _('Your account is activated'))
        else:
            messages.add_message(request, messages.INFO, _('This activation key is already used'))
        return redirect('accounts:login')
    else:
        raise Http404


def reset_email_view(request, key=None):
    q = ResetEmailProfile.objects.filter(key=key)

    if q.exists():
        activation = q.first()
        if not activation.expired:
            user = activation.user
            user.email = activation.new_email
            user.is_active = True
            user.save()
            activation.expired = True
            activation.save()
        return redirect('accounts:login')
    else:
        raise Http404
