# Generated by Django 2.0.3 on 2018-04-01 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djenealog', '0009_auto_20180401_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Divorce',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lieu', models.CharField(blank=True, max_length=50, null=True)),
                ('y', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='année')),
                ('m', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='mois')),
                ('d', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='jour')),
                ('inst', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='djenealog.Couple')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]