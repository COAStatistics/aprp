from django.contrib import admin
from django.forms import ModelForm
from .models import (
    AbstractProduct,
    Config,
    Source,
    Type,
    Unit,
    Chart,
    Festival,
    FestivalName,
    FestivalItems,
)


class AbstractProductModelForm(ModelForm):
    class Meta:
        model = AbstractProduct
        exclude = ['update_time']


class AbstractProductAdmin(admin.ModelAdmin):
    model = AbstractProductModelForm
    list_display = ['id', 'name', 'code', 'config', 'type', 'parent', 'track_item', 'unit']
    list_editable = ['name', 'code', 'track_item']
    list_filter = ('config', 'type', 'track_item')

    search_fields = (
        'id',
        'code',
        'name',
    )


class ConfigModelForm(ModelForm):
    class Meta:
        model = Config
        exclude = ['update_time']


class ConfigAdmin(admin.ModelAdmin):
    model = ConfigModelForm
    list_display = ['id', 'name', 'code', 'update_time']
    list_editable = ['name', 'code']


class SourceModelForm(ModelForm):

    class Meta:
        model = Source
        exclude = ['update_time']


class SourceAdmin(admin.ModelAdmin):
    form = SourceModelForm
    list_display = ['id', 'name', 'alias', 'code', 'update_time']
    list_editable = ['name', 'code']


class TypeModelForm(ModelForm):
    class Meta:
        model = Type
        exclude = ['update_time']


class TypeAdmin(admin.ModelAdmin):
    form = TypeModelForm
    list_display = ['id', 'name', 'update_time']
    list_editable = ['name']


class UnitModelForm(ModelForm):
    class Meta:
        model = Unit
        exclude = ['update_time']


class UnitAdmin(admin.ModelAdmin):
    form = UnitModelForm
    list_display = ['id', 'price_unit', 'volume_unit', 'weight_unit', 'update_time']
    list_editable = ['price_unit', 'volume_unit', 'weight_unit']


class ChartModelForm(ModelForm):
    class Meta:
        model = Unit
        exclude = ['update_time']


class ChartAdmin(admin.ModelAdmin):
    form = UnitModelForm
    list_display = ['id', 'name', 'update_time']
    list_editable = ['name']


class FestivalModelForm(ModelForm):

    class Meta:
        model = Festival
        exclude = ['update_time']


class FestivalAdmin(admin.ModelAdmin):
    form = FestivalModelForm
    list_display = ['id', 'roc_year', 'name', 'enable', 'update_time', 'create_time']
    list_editable = ['roc_year', 'name', 'enable']


class FestivalNameModelForm(ModelForm):

    class Meta:
        model = FestivalName
        exclude = ['update_time']


class FestivalNameAdmin(admin.ModelAdmin):
    form = FestivalNameModelForm
    list_display = ['id',
                    'name',
                    'lunarmonth',
                    'lunarday',
                    'enable',
                    'update_time',
                    'create_time']
    list_editable = ['name',
                    'lunarmonth',
                    'lunarday',
                    'enable']

class FestivalItemsModelForm(ModelForm):

    class Meta:
        model = FestivalItems
        exclude = ['update_time']

class FestivalItemsAdmin(admin.ModelAdmin):
    form = FestivalItemsModelForm
    list_display = ['id', 'order_sn', 'name', 'enable', 'update_time', 'create_time']
    list_editable = ['name', 'enable']
    
admin.site.register(AbstractProduct, AbstractProductAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chart, ChartAdmin)
admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalName, FestivalNameAdmin)
admin.site.register(FestivalItems, FestivalItemsAdmin)