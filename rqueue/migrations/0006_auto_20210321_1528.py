# Generated by Django 3.1.2 on 2021-03-21 13:28

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rqueue', '0005_finishedqueue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finishedqueue',
            name='rqueue',
        ),
        migrations.AddField(
            model_name='finishedqueue',
            name='rqueue_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]