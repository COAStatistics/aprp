from django.contrib import admin
from django.forms import ModelForm
from .models import Cattle


class CattleModelForm(ModelForm):
    class Meta:
        model = Cattle
        exclude = ['update_time']

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class CattleAdmin(admin.ModelAdmin):
    form = CattleModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']


admin.site.register(Cattle, CattleAdmin)
