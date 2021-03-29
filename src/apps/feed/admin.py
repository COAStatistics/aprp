from django.contrib import admin
from django.forms import ModelForm
from .models import Feed


class FeedModelForm(ModelForm):
    class Meta:
        model = Feed
        exclude = ['update_time']

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class FeedAdmin(admin.ModelAdmin):
    form = FeedModelForm
    list_display = ['id', 'name', 'code', 'type', 'parent', 'update_time']
    list_editable = ['name', 'code', 'type', 'parent']


admin.site.register(Feed, FeedAdmin)
