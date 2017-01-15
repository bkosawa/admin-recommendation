# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-22 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleSimilarApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_package', models.CharField(max_length=255)),
                ('similar_package', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'google_similar_app',
                'managed': False,
            },
        ),
    ]