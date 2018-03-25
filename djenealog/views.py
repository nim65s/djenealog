from datetime import date
from django.shortcuts import render

from .models import Individu, Couple, Naissance


def gv(request):
    return render(request, 'djenealog/graph.html', {
        'years': range(Naissance.objects.order_by('y').first().y, date.today().year + 1),
        'individus': Individu.objects.all(),
        'couples': Couple.objects.all(),
    })
