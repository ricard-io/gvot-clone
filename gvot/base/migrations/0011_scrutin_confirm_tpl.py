# Generated by Django 2.2.12 on 2020-05-11 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_emailtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrutin',
            name='confirm_tpl',
            field=models.ForeignKey(blank=True, help_text='Par défaut il en sera fourni un à la création du scrutin. Si le champ est laissé vide, aucun courriel de confirmation ne sera envoyé.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='base.EmailTemplate', verbose_name='Modèle du courriel de confirmation'),
        ),
    ]
