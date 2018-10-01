from datetime import (
    date,
    timedelta,
)
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import (
    Event,
    EventType,
)


def yesterday():
    d = date.today() - timedelta(1)
    return d.strftime('%Y/%m/%d')


class EventForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput)
    content_type = forms.IntegerField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    type = forms.ModelChoiceField(queryset=EventType.objects.all(), empty_label=_("-- Please Select --"), label=_('Event Type'))
    date = forms.DateField(widget=forms.TextInput(attrs={'class': "dateinput"}), initial=yesterday(), label=_('Date'))

    class Meta:
        model = Event
        fields = (
            'id',
            'content_type',
            'object_id',
            'date',
            'type',
            'name',
            'context',
        )
