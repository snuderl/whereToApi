# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-12 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_tiem',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
