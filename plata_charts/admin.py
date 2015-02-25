from django.contrib import admin

from plata_charts import models, forms


class ChartQueryAdmin(admin.ModelAdmin):
    form = forms.ChartQueryForm

    fieldsets = (
        ('Chart specification', {
            'fields': ('name', 'query_json', 'renderer', 'invalidate_cache'),
            'classes': ('grp-collapse grp-closed',),
        }),
        ('Chart dates', {
            'fields': ('start_date', 'end_date', 'step', 'count_type', 'currency'),
        })
    )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('uuid',)


admin.site.register(models.ChartQuery, ChartQueryAdmin)
