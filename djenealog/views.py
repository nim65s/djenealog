from datetime import date
from django.shortcuts import render

from .models import Individu, Couple


def gv(request):
    return render(request, 'djenealog/graph.gv', {
        'years': range(Individu.objects.exclude(naissance_y__lt=1800).order_by('naissance_y').first().naissance_y,
                       date.today().year + 1),
        'individus': Individu.objects.all(),
        'couples': Couple.objects.all(),
    })
