from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model
)
from .models import GroupInformation, ResetEmailProfile
from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

groups = GroupInformation.objects.end_groups()

chValidator = RegexValidator("[^0-9a-zA-Z]", _('Please Input Chinese Only'))


class UserEditForm(forms.ModelForm):
    username = forms.CharField(label=_('Account'))
    first_name = forms.CharField(label=_('First Name'), validators=[chValidator])
    last_name = forms.CharField(label=_('Last Name'), validators=[chValidator])
    group = forms.ModelChoiceField(queryset=groups, label=_('Group'), empty_label=_('Choose one of the following...'))
    reset_email = forms.EmailField(label=_('Reset Email'), required=False)

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True

        if hasattr(self, 'instance'):
            for group in self.instance.groups.all():
                if not group.info.has_child:
                    self.fields['group'].initial = group.info.id

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'reset_email',
            'first_name',
            'last_name',
            'group'
        ]

    def clean(self, *args, **kwargs):
        user = self.instance
        group = self.cleaned_data.get("group")
        email = self.cleaned_data.get('email')
        reset_email = self.cleaned_data.get('reset_email')
        if reset_email != "":
            if reset_email != user.email:
                email_qs = User.objects.filter(email=reset_email)
                if email_qs.exists():
                    self.add_error('reset_email', _('This email has already been registered'))
                else:
                    ResetEmailProfile.objects.create(user=user, new_email=reset_email)
        else:
            dns = email.split('@')[1]
            if dns != group.email_dns:
                self.add_error('group', (_('To use this group, please change your email to this unit:') + group.name))
        return super(UserEditForm, self).clean(*args, **kwargs)

    def save(self, commit=True):
        form = super(UserEditForm, self).save(commit=False)

        if commit:
            user = self.instance
            group_info = self.cleaned_data.get('group')
            # Remove previous groups and assign to new groups
            for info in GroupInformation.objects.all():
                if info in group_info.parents():
                    info.group.user_set.add(user)
                else:
                    info.group.user_set.remove(user)
            form.save()
        return form


class UserLoginForm(forms.Form):
    username = forms.CharField(label=_('Account'), help_text=_('Please enter your account'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'), help_text=_('Please enter your password'))
    remember = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    # This field just for identity validate inactive error in views.py
    is_active = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username == 'guest':
            raise forms.ValidationError(_('Guest account will no longer accessible. Please feel free to register new account'))

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(_('Your account or password is incorrect'))
            if not user.is_active:
                self.cleaned_data['is_active'] = False
                raise forms.ValidationError(
                    mark_safe(
                        '{}<p><br><a href="{}" class="btn btn-sm btn-default">{}</a></p>'.format(
                            _('Please activate your account'),
                            reverse('accounts:activation_resend'),
                            _('Resend Activation Email')
                        )
                    )
                )

        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label=_('Account'), help_text=_('Please enter your account'))
    email = forms.EmailField(label=_('Email'), help_text=_('Please enter your email'))
    first_name = forms.CharField(label=_('First Name'), validators=[chValidator])
    last_name = forms.CharField(label=_('Last Name'), validators=[chValidator])
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'), help_text=_('Please enter your password'))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Confirm Password'), help_text=_('Please confirm your password'))
    condition = forms.BooleanField(required=True, widget=forms.CheckboxInput(), label=_('Terms & Conditions'))

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'last_name',
            'first_name',
            'password',
            'password2',
            'condition',
        ]

    def clean_condition(self):
        condition = self.cleaned_data.get('condition')
        if not condition:
            raise forms.ValidationError(_('You must agree our terms and conditions'))
        return condition

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError(_('Password must match'))
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # restrict email dns
        dns = email.split('@')[1]
        if not GroupInformation.objects.filter(email_dns=dns).count():
            raise forms.ValidationError(_('Please register with email under domain "@mail.coa.gov.tw"'))

        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError(_('This email has already been registered'))
        return email


class UserResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label=_('Password'), help_text=_('Please enter your password'))
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label=_('Confirm Password'), help_text=_('Please confirm your password'))

    class Meta:
        model = User
        fields = [
            'password',
            'password2'
        ]

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError(_('Password must match'))
        return password


class ResendEmailForm(forms.Form):
    email = forms.EmailField(required=False, label=_('Email'), help_text=_('Please enter your email'))
    username = forms.CharField(required=False, label=_('Account'), help_text=_('Please enter your account'))

    class Meta:
        model = User
        fields = [
            'email',
            'username',
        ]

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email == '' and username == '':
            raise forms.ValidationError(_('Please advise your email or account'))

        if email and username:
            user = User.objects.filter(email=email, username=username).first()
            if not user:
                raise forms.ValidationError(_('Your account or email is incorrect'))

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_qs = User.objects.filter(email=email)
            if not email_qs.exists():
                raise forms.ValidationError(_('This email is not exist'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username_qs = User.objects.filter(username=username)
            if not username_qs.exists():
                raise forms.ValidationError(_('This account is not exist'))
        return username
