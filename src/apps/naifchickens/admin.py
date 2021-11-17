from django.contrib import admin
from django.forms import ModelForm
from .models import Naifchickens


class NaifchickensModelForm(ModelForm):
    class Meta:
        model = Naifchickens
        exclude = ['update_time']

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class NaifchickensAdmin(admin.ModelAdmin):
    form = NaifchickensModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']


admin.site.register(Naifchickens, NaifchickensAdmin)
