import django_tables2 as tables

from . import models


class IndividuTable(tables.Table):
    edit = tables.Column(accessor='get_link', orderable=False)

    class Meta:
        model = models.Individu
        fields = ('prenom', 'nom', 'masculin', 'parents', 'edit')

    def render_masculin(self, value):
        return '♂' if value else '♀'


class CoupleTable(tables.Table):
    edit = tables.Column(accessor='get_link', orderable=False)

    class Meta:
        model = models.Couple
        fields = ('mari', 'femme', 'edit')
