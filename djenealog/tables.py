import django_tables2 as tables

from . import models


class IndividuTable(tables.Table):
    link = tables.Column(accessor='get_link', orderable=False)

    class Meta:
        model = models.Individu
        fields = ('prenom', 'nom', 'link')


class CoupleTable(tables.Table):
    class Meta:
        model = models.Couple
        fields = ('mari', 'femme')
