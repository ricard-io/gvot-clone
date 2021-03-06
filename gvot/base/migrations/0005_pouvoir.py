# Generated by Django 2.2.10 on 2020-02-21 17:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_scrutins'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pouvoir',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('courriel', models.EmailField(max_length=254)),
                ('scrutin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Scrutin')),
            ],
        ),
    ]
