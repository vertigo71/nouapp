# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nouapp', '0002_nou_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nou',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
