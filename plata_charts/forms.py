import importlib
import json

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from datetimewidget.widgets import DateWidget
from datetime import datetime
from django.utils import timezone

from plata_charts import models


widget_options = {
    'format': 'yyyy-mm-dd',
    'autoclose': True,
    'weekStart': 1
}


class ChartQueryForm(forms.ModelForm):
    invalidate_cache = forms.BooleanField(initial=False, required=False)

    def save(self, commit=True):
        if self.cleaned_data.get('invalidate_cache', False):
            self.instance.invalidate_cache()
        return forms.ModelForm.save(self, commit=commit)

    class Meta:
        model = models.ChartQuery


class ChartForm(forms.Form):
    uuid = forms.CharField(widget=forms.HiddenInput())
    products = forms.MultipleChoiceField(label="Products", widget=forms.SelectMultiple(attrs={'size': 14}))
    start_date = forms.DateField(label="Start date",
                                 required=False,
                                 widget=DateWidget(options=widget_options))
    end_date = forms.DateField(label="End date",
                               required=False,
                               widget=DateWidget(options=widget_options))
    step = forms.ChoiceField(label="Chart step",
                             initial=1,
                             choices=[(0, "Yearly"), (1, "Monthly"), (2, "Weekly"), (3, "Daily")])
    renderer = forms.ChoiceField(label="Renderer",
                                 initial="jqplot",
                                 choices=[("canvasjs", "CanvasJS"), ("jqplot", "jqPlot"), ("chartjs", "chart.js")])

    def __init__(self, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        forms.Form.__init__(self, *args, **kwargs)
        product_module, product_class = settings.PLATA_SHOP_PRODUCT.rsplit('.', 1)
        product_module = importlib.import_module(product_module + ".models")
        product_class = getattr(product_module, product_class)
        products = self.fields['products']
        products.choices = [(p.pk, str(p)) for p in product_class.products.all()]

        if not self.fields['uuid'].initial and uuid:
            self.fields['uuid'].initial = uuid

    def build_chart_url(self):
        uuid = self.cleaned_data['uuid']
        products = self.cleaned_data['products']
        start_date = self.cleaned_data.get('start_date', None)
        end_date = self.cleaned_data.get('end_date', None)

        params = {
            'step': self.cleaned_data['step'],
            'renderer': self.cleaned_data['renderer']
        }

        if start_date:
            params['start_date'] = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.UTC()).isoformat()
        if end_date:
            params['end_date'] = datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.UTC()).isoformat()

        if len(products) == 1:
            params['product_filter'] = json.dumps({'product__pk': products[0]})
        else:
            params['product_filter'] = json.dumps({'product__pk__in': products})

        url = reverse('plata_charts_chart', args=[uuid])

        return url, mark_safe(json.dumps(params))
