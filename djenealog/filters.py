import django_filters as filters

from . import models


class IndividuFilter(filters.FilterSet):
    nom = filters.CharFilter(lookup_expr='icontains')
    prenom = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Individu
        fields = ('nom', 'prenom')


class CoupleFilter(filters.FilterSet):
    mari = filters.CharFilter(lookup_expr='__nom__icontains')
    femme = filters.CharFilter(lookup_expr='__nom__icontains')

    class Meta:
        model = models.Couple
        fields = ('mari', 'femme')
