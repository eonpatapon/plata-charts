from django.conf.urls import patterns, url

import plata_charts.views as views

urlpatterns = patterns(
    '',
    #url(r'^report/$', views.report, name='plata_charts'),
    #url(r'^report/form/(?P<uuid>[^/]*)/$', views.report_form, name='plata_charts_form'),
    url(r'^report/chart/(?P<uuid>[^/]*)/$', views.report_chart, name='plata_charts_chart')
)
