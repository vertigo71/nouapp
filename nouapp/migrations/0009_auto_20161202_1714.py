# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 16:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nouapp', '0008_log'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Log',
            new_name='LogActivity',
        ),
    ]
