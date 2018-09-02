import django_filters as filters

from . import models


class IndividuFilter(filters.FilterSet):
    nom = filters.CharFilter(lookup_expr='icontains')
    prenom = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Individu
        fields = ('nom', 'prenom')


class CoupleFilter(filters.FilterSet):
    mari__nom = filters.CharFilter(lookup_expr='icontains')
    femme__nom = filters.CharFilter(lookup_expr='icontains')
    mari__prenom = filters.CharFilter(lookup_expr='icontains')
    femme__prenom = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Couple
        fields = ('mari__nom', 'mari__prenom', 'femme__nom', 'femme__prenom')
