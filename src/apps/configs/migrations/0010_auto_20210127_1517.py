# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2021-01-27 07:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configs', '0009_auto_20201027_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='festivalname',
            name='lunarday',
            field=models.CharField(default='01', max_length=2, verbose_name='LunarDay'),
        ),
        migrations.AddField(
            model_name='festivalname',
            name='lunarmonth',
            field=models.CharField(default='01', max_length=2, verbose_name='LunarMonth'),
        ),
        migrations.AlterField(
            model_name='festival',
            name='roc_year',
            field=models.CharField(default=110, max_length=3, verbose_name='ROC Year'),
        ),
    ]