# Generated by Django 2.2.19 on 2021-03-04 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_courriel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pouvoir',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='pouvoir',
            name='courriel',
        ),
    ]
