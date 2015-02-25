import logging

from uuid import uuid4
from datetime import datetime

from django.utils import timezone
from django.db import models

from plata.fields import JSONField, CurrencyField


logger = logging.getLogger(__name__)


def generateUUID():
        return str(uuid4())


class ChartQuery(models.Model):
    COUNT_INCOME = 0
    COUNT_ORDERS = 1

    name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255, default=generateUUID)
    query_json = JSONField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    step = models.IntegerField(choices=((0, 'Yearly'), (1, 'Monthly'), (2, 'Weekly'), (3, 'Daily')), default=1)
    renderer = models.CharField(choices=(('chartjs', 'Chart.js'), ('canvasjs', 'CanvasJS'), ('jqplot', 'jqPlot')), max_length=255, default='canvasjs')
    count_type = models.IntegerField(choices=((COUNT_INCOME, 'Income'), (COUNT_ORDERS, 'Number of orders')), default=0)
    currency = CurrencyField(default="EUR")

    def __unicode__(self):
        return self.name

    @property
    def start_date_iso(self):
        """
        Return a offset-aware date in iso format
        """
        if self.start_date:
            return datetime(self.start_date.year, self.start_date.month, self.start_date.day, tzinfo=timezone.UTC()).isoformat()
        return ""

    @property
    def end_date_iso(self):
        """
        Return a offset-aware date in iso format
        """
        if self.end_date:
            return datetime(self.end_date.year, self.end_date.month, self.end_date.day, tzinfo=timezone.UTC()).isoformat()
        return ""

    def invalidate_cache(self):
        try:
            ChartCache.objects.get(uuid=self.uuid, step=self.step).delete()
            logger.debug("Chart cache deleted")
        except ChartCache.DoesNotExist:
            pass
        return True

    @property
    def invalidate_cache_fields(self):
        """
        Return the list of fields that requires to remove the chart cache
        when changed.
        """
        return ('query_json', 'currency')

    def save(self, *args, **kwargs):
        """
        Check if the chart cache must be removed before updating
        the DB.
        """
        if self.pk is not None:
            orig = ChartQuery.objects.get(pk=self.pk)
            for field in self.invalidate_cache_fields:
                if getattr(self, field) != getattr(orig, field):
                    self.invalidate_cache()
                    # Handle the currency directly in the filter
                    if field == "currency":
                        self.query_json['order__currency'] = self.currency
        return models.Model.save(self, *args, **kwargs)

    class Meta:
        verbose_name = "Chart Query"
        verbose_name_plural = "Chart Queries"


class ChartCache(models.Model):
    uuid = models.CharField(max_length=255)
    step = models.IntegerField(choices=((0, 'Yearly'), (1, 'Monthly'), (2, 'Weekly'), (3, 'Daily')), default=1)
    cache = JSONField()
