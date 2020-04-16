from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import (ActivationProfile,
                     GroupInformation,
                     UserInformation,
                     ResetPasswordProfile,
                     ResetEmailProfile,
                     AbstractProfile)


class GroupListFilter(SimpleListFilter):
    title = _('Group')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [(group.id, group.name) for group in Group.objects.all()]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or 'other')
        # to decide how to filter the queryset.
        if self.value():
            return queryset.filter(user__groups__id=self.value())
        else:
            return queryset


class UserInformationAdmin(admin.ModelAdmin):
    model = UserInformation
    list_filter = (
        GroupListFilter,
        'amislist_viewer'
    )
    search_fields = (
        'id',
        'user__first_name',
        'user__last_name',
        'user__username'
    )


admin.site.register(ActivationProfile)
admin.site.register(GroupInformation)
admin.site.register(UserInformation, UserInformationAdmin)
admin.site.register(ResetPasswordProfile)
admin.site.register(ResetEmailProfile)
admin.site.register(AbstractProfile)
