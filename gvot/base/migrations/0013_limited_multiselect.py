# Generated by Django 2.2.12 on 2020-06-02 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_validators_on_emailtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfield',
            name='max_values',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Nombre maximal de valeurs à choisir pour le champ de sélection multiple bornée', null=True, verbose_name='Valeurs max'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='min_values',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Nombre minimal de valeurs à choisir pour le champ de sélection multiple bornée', null=True, verbose_name='Valeurs min'),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.CharField(choices=[('singleline', 'Single line text'), ('multiline', 'Multi-line text'), ('email', 'Email'), ('number', 'Number'), ('url', 'URL'), ('checkbox', 'Checkbox'), ('checkboxes', 'Choix multiples'), ('dropdown', 'Drop down'), ('multiselect', 'Multiple select'), ('radio', 'Radio buttons'), ('date', 'Date'), ('lim_multiselect', 'Sélection multiple bornée')], max_length=16, verbose_name='field type'),
        ),
    ]
