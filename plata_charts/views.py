import sys
import json
import traceback

import dateutil.parser

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse

from plata_charts.models import ChartQuery
from plata_charts.forms import ChartForm
from plata_charts.lib import NoProductOrders, product_orders
from plata_charts.tb import full_exc_info


def report(request):
    return render(request, template_name='plata_charts/report.html')


def report_form(request, uuid):
    """
    Chart form view

    On POST, validate the form and return url and params to render the chart.

    @type uuid: str
    """
    c = {'uuid': uuid}

    if request.method == 'POST':
        form = ChartForm(request.POST)
        if form.is_valid():
            # build chart form URL
            c['chart_url'], c['chart_params'] = form.build_chart_url()
    else:
        form = ChartForm(uuid=uuid)

    c['form'] = form

    return render(request, template_name='plata_charts/report_form.html',
                  context_instance=RequestContext(request, c))


def report_chart(request, uuid):
    """
    Chart generation view

    @type uuid: str
    @type query_filter: dict
    @type start_date: isoformat date
    @type end_date: isoformat date
    @type step: int
    @param renderer: library used to draw the graph
    @type renderer: string
    @param count_type: data type to count
    @type count_type: str
    """
    type = "line"

    try:
        chart = ChartQuery.objects.get(uuid=uuid)
        filter_dict = chart.query_json
        start_date = chart.start_date_iso
        end_date = chart.end_date_iso
        step = chart.step
        renderer = chart.renderer
        count_type = chart.count_type
    except ChartQuery.DoesNotExist:
        filter_dict = json.loads(request.GET.get('filter_dict'))
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        step = int(request.GET.get('step', 1))
        renderer = request.GET.get('renderer', 'canvasjs')
        count_type = int(request.GET.get('count_type', 0))

    if start_date:
        start_date = dateutil.parser.parse(start_date)
    else:
        start_date = None
    if end_date:
        end_date = dateutil.parser.parse(end_date)
    else:
        end_date = None

    try:
        range, orders = product_orders(uuid, filter_dict, start_date, end_date, step, count_type)
    except NoProductOrders:
        return HttpResponse(content="No orders found", status=500)
    except:
        tb = "".join(traceback.format_exception(*full_exc_info()))
        return HttpResponse(content="<strong>Graph generation failed :</strong><br /><pre>%(tb)s</pre>" % {'tb': tb}, status=500)

    return render(request, template_name='plata_charts/product_%s_chart.html' % type,
                  context_instance=RequestContext(request, {'uuid': uuid,
                                                            'step': step,
                                                            'filter_dict': filter_dict,
                                                            'count_type': count_type,
                                                            'renderer': renderer,
                                                            'orders': orders,
                                                            'range': range}))
