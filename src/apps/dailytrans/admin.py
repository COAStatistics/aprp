from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import DailyTran, DailyReport
from rangefilter.filter import DateRangeFilter


class DailyTranModelForm(ModelForm):
    class Meta:
        model = DailyTran
        exclude = []

    def clean(self):
        product = self.cleaned_data.get('product')
        source = self.cleaned_data.get('source')
        valid = True
        if not product:
            raise ValidationError('There is no such content object')

        try:
            if source.config != product.config:
                valid = False
        except AttributeError:
            pass

        try:
            if source.config.id != product.category.config.id:
                valid = False
        except AttributeError:
            pass

        if not valid:
            raise ValidationError("Source are incorrect")

        return self.cleaned_data


class DailyTranAdmin(admin.ModelAdmin):
    form = DailyTranModelForm
    list_display = ('date',
                    'update_time',
                    'create_time',
                    'not_updated',
                    'product',
                    'source',
                    'up_price',
                    'mid_price',
                    'low_price',
                    'avg_price',
                    'avg_weight',
                    'volume')
    list_editable = ('up_price', 'mid_price', 'low_price', 'avg_price', 'avg_weight', 'volume')
    list_filter = (('date', DateRangeFilter), 'product__config__name', 'source')
    search_fields = ['product__name']


class DailyReportAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'update_time',
        'create_time',
    )


admin.site.register(DailyTran, DailyTranAdmin)
admin.site.register(DailyReport, DailyReportAdmin)
