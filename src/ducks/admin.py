from django.contrib import admin
from django.forms import ModelForm
from .models import Duck


class DuckModelForm(ModelForm):
    class Meta:
        model = Duck
        exclude = ['update_time']

    def clean(self):
        cleaned_data = self.cleaned_data
        print(cleaned_data)
        return cleaned_data


class DuckAdmin(admin.ModelAdmin):
    form = DuckModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']


admin.site.register(Duck, DuckAdmin)
