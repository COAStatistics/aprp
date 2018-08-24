from django.contrib import admin
from django.forms import ModelForm
from django.forms import TextInput
from django.db import models
from .models import Flower


class FlowerModelForm(ModelForm):
    class Meta:
        model = Flower
        exclude = ['update_time']


class FlowerAdmin(admin.ModelAdmin):
    form = FlowerModelForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }
    list_display = ['id', 'name', 'code', 'type', 'parent', 'track_item', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent', 'track_item']


admin.site.register(Flower, FlowerAdmin)