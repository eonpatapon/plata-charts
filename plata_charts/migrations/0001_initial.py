# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChartQuery'
        db.create_table(u'plata_charts_chartquery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='318f8b8d-1c66-431a-a150-31b9a7dcda06', max_length=255)),
            ('query_json', self.gf('plata.fields.JSONField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('step', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('renderer', self.gf('django.db.models.fields.CharField')(default='chartjs', max_length=255)),
        ))
        db.send_create_signal(u'plata_charts', ['ChartQuery'])

        # Adding model 'ChartCache'
        db.create_table(u'plata_charts_chartcache', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('step', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('cache', self.gf('plata.fields.JSONField')()),
        ))
        db.send_create_signal(u'plata_charts', ['ChartCache'])


    def backwards(self, orm):
        # Deleting model 'ChartQuery'
        db.delete_table(u'plata_charts_chartquery')

        # Deleting model 'ChartCache'
        db.delete_table(u'plata_charts_chartcache')


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
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'query_json': ('plata.fields.JSONField', [], {}),
            'renderer': ('django.db.models.fields.CharField', [], {'default': "'chartjs'", 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'c8e58112-30f4-4c82-98c1-0c9f570edc8e'", 'max_length': '255'})
        }
    }

    complete_apps = ['plata_charts']