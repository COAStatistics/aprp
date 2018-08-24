from django.contrib import admin
from django.forms import ModelForm
from .models import Rice


class RiceModelForm(ModelForm):
    class Meta:
        model = Rice
        exclude = ['update_time']


class RiceAdmin(admin.ModelAdmin):
    form = RiceModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']
    readonly_fields = ['config']


admin.site.register(Rice, RiceAdmin)
