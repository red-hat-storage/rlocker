# Generated by Django 3.2 on 2022-06-20 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lockable_resource", "0007_lockableresource_associated_queue"),
    ]

    operations = [
        migrations.AddField(
            model_name="lockableresource",
            name="locked_time",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
