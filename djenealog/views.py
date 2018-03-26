from datetime import date
from django.shortcuts import render
from django.views.generic import UpdateView

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from . import models, tables, filters


def gv(request):
    return render(request, 'djenealog/graph.html', {
        'years': range(models.Naissance.objects.order_by('y').first().y, date.today().year + 1),
        'individus': models.Individu.objects.all(),
        'couples': models.Couple.objects.all(),
    })


class IndividusView(SingleTableMixin, FilterView):
    model = models.Individu
    table_class = tables.IndividuTable
    filterset_class = filters.IndividuFilter


class CouplesView(SingleTableMixin, FilterView):
    model = models.Couple
    table_class = tables.CoupleTable
    filterset_class = filters.CoupleFilter


class IndividuView(UpdateView):
    model = models.Individu
    fields = ('nom', 'prenom', 'masculin', 'parents')


class CoupleView(UpdateView):
    model = models.Couple
    fields = ('mari', 'femme')
