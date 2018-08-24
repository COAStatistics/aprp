from django.contrib import admin
from django.forms import ModelForm
from .models import Chicken


class ChickenModelForm(ModelForm):
    class Meta:
        model = Chicken
        exclude = ['update_time']

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class ChickenAdmin(admin.ModelAdmin):
    form = ChickenModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']


admin.site.register(Chicken, ChickenAdmin)
