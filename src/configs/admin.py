from django.contrib import admin
from django.forms import ModelForm
from .models import (
    AbstractProduct,
    Config,
    Source,
    Type,
    Unit,
    Chart
)


class AbstractProductModelForm(ModelForm):
    class Meta:
        model = AbstractProduct
        exclude = ['update_time']


class AbstractProductAdmin(admin.ModelAdmin):
    model = AbstractProductModelForm
    list_display = ['id', 'name', 'code', 'config', 'type', 'parent', 'track_item', 'unit']
    list_editable = ['name', 'code', 'track_item']


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
    list_display = ['id', 'name', 'code', 'update_time']
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


admin.site.register(AbstractProduct, AbstractProductAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chart, ChartAdmin)
