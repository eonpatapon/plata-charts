from __future__ import absolute_import

import json

from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

from plata_charts.lib import random_colors


register = template.Library()


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))


def format_count(count):
    return float("{0:.2f}".format(count))


@register.filter
def json_safe(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return mark_safe(json.dumps(object))


@register.assignment_tag
def to_canvasjs(orders, range):
    data = []
    for product, counts in orders.items():
        serie = {
            'name': product,
            'showInLegend': True,
            'type': 'spline',
            'dataPoints': []
        }
        for count, date in zip(counts, range):
            serie['dataPoints'].append({
                'x': date,
                'y': format_count(count)
            })
        data.append(serie)
    return mark_safe(json.dumps(data, default=handler))


@register.assignment_tag
def to_jqplot(orders, range):
    jqplot_data = {
        'data': [],
        'series': []
    }
    for product, counts in orders.items():
        serie = []
        for count, date in zip(counts, range):
            serie.append([date, format_count(count)])
        jqplot_data['data'].append(serie)
        jqplot_data['series'].append({'label': product})
    return mark_safe(json.dumps(jqplot_data, default=handler))


@register.assignment_tag
def to_chartjs(orders, range):
    nb_products = len(orders.keys())
    fill_color = []
    highlight_fill = []
    stroke_color = []
    for r, g, b in random_colors(nb_products):
        fill_color.append("rgba(%i, %i, %i, 0.2" % (r, g, b))
        highlight_fill.append("rgba(%i, %i, %i, 0.5" % (r, g, b))
        stroke_color.append("rgba(%i, %i, %i, 1" % (r, g, b))
    chartjs_data = {
        'labels': range,
        'datasets': []
    }
    index = 0
    for product, counts in orders.items():
        serie = {
            'label': product,
            'fillColor': fill_color[index],
            'pointColor': stroke_color[index],
            'strokeColor': stroke_color[index],
            'highlightFill': highlight_fill[index],
            'highlightStroke': stroke_color[index],
            'data': []
        }
        for count, date in zip(counts, range):
            serie['data'].append(format_count(count))
        chartjs_data['datasets'].append(serie)
        index += 1
    return mark_safe(json.dumps(chartjs_data, default=handler))


@register.inclusion_tag("plata_charts/_line_chart.html", takes_context=True)
def render_line_chart(context):
    context['template'] = "plata_charts/_%s_line_chart.html" % context.get('renderer', 'canvasjs')
    return context
