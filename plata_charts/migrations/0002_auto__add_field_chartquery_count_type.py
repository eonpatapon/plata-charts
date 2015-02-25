# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ChartQuery.count_type'
        db.add_column(u'plata_charts_chartquery', 'count_type',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ChartQuery.count_type'
        db.delete_column(u'plata_charts_chartquery', 'count_type')


    models = {
        u'plata_charts.chartcache': {
            'Meta': {'object_name': 'ChartCache'},
            'cache': ('plata.fields.JSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'plata_charts.chartquery': {
            'Meta': {'object_name': 'ChartQuery'},
            'count_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'query_json': ('plata.fields.JSONField', [], {}),
            'renderer': ('django.db.models.fields.CharField', [], {'default': "'canvasjs'", 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'588dbbaf-dab9-499a-aad7-f47bccbf0f67'", 'max_length': '255'})
        }
    }

    complete_apps = ['plata_charts']