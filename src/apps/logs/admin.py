from __future__ import unicode_literals
import logging

from django.contrib import admin
from django.utils.html import format_html

from .models import Log, LogType


class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('colored_msg', 'create_datetime', 'type', 'url', 'duration', 'traceback')
    list_display_links = ('colored_msg', 'url')
    list_filter = ('level', 'type__name', )
    list_per_page = 10

    def colored_msg(self, instance):
        if instance.level in [logging.NOTSET, logging.INFO]:
            color = 'green'
        elif instance.level in [logging.WARNING, logging.DEBUG]:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {color};">{msg}</span>', color=color, msg=instance.msg)
    colored_msg.short_description = 'Message'

    def traceback(self, instance):
        return format_html('<pre><code>{content}</code></pre>', content=instance.trace if instance.trace else '')


admin.site.register(Log, StatusLogAdmin)
admin.site.register(LogType)
