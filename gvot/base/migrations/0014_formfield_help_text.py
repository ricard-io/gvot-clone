# Generated by Django 2.2.12 on 2020-06-04 18:19

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_limited_multiselect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='help_text',
            field=wagtail.core.fields.RichTextField(blank=True, verbose_name="texte d'aide"),
        ),
    ]
