from datetime import (
    date,
    timedelta,
)
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Event


def yesterday():
    d = date.today() - timedelta(1)
    return d.strftime('%Y/%m/%d')


class EventForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput)
    content_type = forms.IntegerField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    date = forms.DateField(widget=forms.TextInput(attrs={'data-datepicker': "true"}),
                           initial=yesterday(), label=_('Date'))
    share = forms.BooleanField(label=_('Share this event'))

    class Meta:
        model = Event
        fields = (
            'id',
            'content_type',
            'object_id',
            'date',
            'types',
            'name',
            'context',
            'share',
        )
