from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import (
    Watchlist,
    WatchlistItem,
    MonitorProfile,
)


class MonitorProfileModelForm(ModelForm):
    class Meta:
        model = MonitorProfile
        exclude = ['update_date']


class MonitorProfileAdmin(admin.ModelAdmin):
    form = MonitorProfileModelForm
    list_display = ['id', 'product', 'watchlist', 'active', 'price', 'color', 'info', 'period', 'action']


class WatchlistItemModelForm(ModelForm):
    class Meta:
        model = WatchlistItem
        exclude = ['update_date']

    def clean(self):
        product = self.cleaned_data.get('product')

        if not product:
            raise ValidationError('Can not find this product')

        if product.has_child:
            raise ValidationError('Not a allowed object, please advise a child product')

        valid_sources = product.sources()
        sources = self.cleaned_data.get('sources')
        for source in sources:
            if source not in valid_sources:
                raise ValidationError('%s is not a valid source for this object' % source)

        return self.cleaned_data


class WatchlistItemAdmin(admin.ModelAdmin):
    form = WatchlistItemModelForm
    list_display = ['id', 'product', 'update_time']


class WatchlistModelForm(ModelForm):
    class Meta:
        model = Watchlist
        exclude = ['update_date']


class WatchlistAdmin(admin.ModelAdmin):
    form = WatchlistModelForm
    list_display = ['id', 'name', 'user', 'is_default', 'watch_all', 'update_time']
    list_editable = ['name', 'user']


admin.site.register(WatchlistItem, WatchlistItemAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(MonitorProfile, MonitorProfileAdmin)

