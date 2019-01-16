from django.contrib import admin
from django.forms import ModelForm
from django.forms import TextInput
from django.db import models
from .models import Crop


class CropModelForm(ModelForm):
    class Meta:
        model = Crop
        exclude = ['update_time']


class CropAdmin(admin.ModelAdmin):
    form = CropModelForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }
    list_display = ['id', 'name', 'code', 'type', 'parent', 'track_item', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent', 'track_item']


admin.site.register(Crop, CropAdmin)
