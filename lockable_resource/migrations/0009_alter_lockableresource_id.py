# Generated by Django 3.2 on 2022-08-07 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lockable_resource', '0008_lockableresource_locked_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockableresource',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]