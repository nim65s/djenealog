# Generated by Django 2.2.4 on 2019-09-29 16:56

import autoslug.fields
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import ndh.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Couple",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("debut", models.DateField(blank=True, null=True)),
                ("fin", models.DateField(blank=True, null=True)),
                ("commentaires", models.TextField(blank=True, null=True)),
            ],
            bases=(models.Model, ndh.models.Links),
        ),
        migrations.CreateModel(
            name="Individu",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(blank=True, max_length=50)),
                (
                    "prenom",
                    models.CharField(blank=True, max_length=50, verbose_name="Prénom"),
                ),
                (
                    "usage",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="Prénom d’usage"
                    ),
                ),
                (
                    "epouse",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Nom d’épouse ou d’usage",
                    ),
                ),
                ("masculin", models.NullBooleanField()),
                ("wikidata", models.PositiveIntegerField(blank=True, null=True)),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "parents",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="enfants",
                        to="djenealog.Couple",
                    ),
                ),
            ],
            bases=(models.Model, ndh.models.Links),
        ),
        migrations.CreateModel(
            name="Lieu",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        editable=False, populate_from="name", unique=True
                    ),
                ),
                ("wikidata", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "point",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, geography=True, null=True, srid=4326
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Lieux",
            },
            bases=(ndh.models.Links, models.Model),
        ),
        migrations.CreateModel(
            name="Pacs",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="année"
                    ),
                ),
                (
                    "m",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="mois"
                    ),
                ),
                (
                    "d",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="jour"
                    ),
                ),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "inst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Couple",
                    ),
                ),
                (
                    "lieu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Lieu",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "pacs",
            },
        ),
        migrations.CreateModel(
            name="Naissance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="année"
                    ),
                ),
                (
                    "m",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="mois"
                    ),
                ),
                (
                    "d",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="jour"
                    ),
                ),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "inst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Individu",
                    ),
                ),
                (
                    "lieu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Lieu",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Mariage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="année"
                    ),
                ),
                (
                    "m",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="mois"
                    ),
                ),
                (
                    "d",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="jour"
                    ),
                ),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "inst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Couple",
                    ),
                ),
                (
                    "lieu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Lieu",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Divorce",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="année"
                    ),
                ),
                (
                    "m",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="mois"
                    ),
                ),
                (
                    "d",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="jour"
                    ),
                ),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "inst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Couple",
                    ),
                ),
                (
                    "lieu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Lieu",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Deces",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="année"
                    ),
                ),
                (
                    "m",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="mois"
                    ),
                ),
                (
                    "d",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="jour"
                    ),
                ),
                ("commentaires", models.TextField(blank=True, null=True)),
                (
                    "inst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Individu",
                    ),
                ),
                (
                    "lieu",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="djenealog.Lieu",
                    ),
                ),
            ],
            options={
                "verbose_name": "décès",
                "verbose_name_plural": "décès",
            },
        ),
        migrations.AddField(
            model_name="couple",
            name="femme",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="femme",
                to="djenealog.Individu",
            ),
        ),
        migrations.AddField(
            model_name="couple",
            name="mari",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="mari",
                to="djenealog.Individu",
            ),
        ),
    ]
