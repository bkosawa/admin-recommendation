# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-03-16 12:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0005_userapps'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRecommendedApps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.App')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.User')),
            ],
            options={
                'db_table': 'user_recommended_apps',
                'managed': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='userrecommendedapps',
            unique_together=set([('user', 'app')]),
        ),
    ]