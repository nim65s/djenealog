from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, UpdateView

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from ndh.mixins import SuperUserRequiredMixin

from . import filters, forms, models, tables


@login_required
def gv(request):
    fmt = request.GET.get('fmt', 'html')
    return render(request, f'djenealog/graph.{fmt}', {
        'years': range(models.Naissance.objects.exclude(y=None).order_by('y').first().y, date.today().year + 1),
        'individus': models.Individu.objects.all(),
        'couples': models.Couple.objects.all(),
    })


def stats(request):
    prenom, usage, nom, epouse = [
        {
            row[field]: row['total']
            for row in models.Individu.objects.all().values(field).annotate(total=Count(field)) if row[field] != ''
        }
        for field in ('prenom', 'usage', 'nom', 'epouse')
    ]
    noms, prenoms = set(list(nom.keys()) + list(epouse.keys())), set(list(prenom.keys()) + list(usage.keys()))
    noms = [(nom.get(n, 0) + epouse.get(n, 0), nom.get(n, 0), epouse.get(n, 0), n) for n in noms if n != '']
    prenoms = [(prenom.get(n, 0) + usage.get(n, 0), prenom.get(n, 0), usage.get(n, 0), n) for n in prenoms if n != '']

    centenaires = models.Individu.objects.filter(deces__isnull=True, naissance__y__lt=date.today().year - 100)
    maris_pas_masculins = models.Couple.objects.exclude(mari__masculin=True).exclude(mari__isnull=True)
    femmes_pas_feminines = models.Couple.objects.exclude(femme__masculin=False).exclude(femme__isnull=True)
    divorces_sans_mariages = models.Couple.objects.filter(divorce__isnull=False, mariage__isnull=True)

    return render(request, 'djenealog/stats.html', {
        'individus': models.Individu.objects.count(),
        'couples': models.Couple.objects.count(),
        'naissances': models.Naissance.objects.count(),
        'baptemes': models.Bapteme.objects.count(),
        'deces': models.Deces.objects.count(),
        'mariages': models.Mariage.objects.count(),
        'divorces': models.Divorce.objects.count(),
        'pacs': models.Pacs.objects.count(),
        'noms': sorted(noms, reverse=True),
        'prenoms': sorted(prenoms, reverse=True),
        'hommes': models.Individu.objects.filter(masculin=True).count(),
        'femmes': models.Individu.objects.filter(masculin=False).count(),
        'centenaires': centenaires.count(),
        'maris_pas_masculins': maris_pas_masculins.count(),
        'femmes_pas_feminines': femmes_pas_feminines.count(),
        'divorces_sans_mariages': divorces_sans_mariages.count(),
    })


class IndividusView(SuperUserRequiredMixin, SingleTableMixin, FilterView):
    model = models.Individu
    table_class = tables.IndividuTable
    filterset_class = filters.IndividuFilter


class CouplesView(SuperUserRequiredMixin, SingleTableMixin, FilterView):
    model = models.Couple
    table_class = tables.CoupleTable
    filterset_class = filters.CoupleFilter


class IndividuView(SuperUserRequiredMixin, UpdateView):
    model = models.Individu
    form_class = forms.IndividuForm


class CoupleView(SuperUserRequiredMixin, UpdateView):
    model = models.Couple
    form_class = forms.CoupleForm


class IndividuCreateView(SuperUserRequiredMixin, CreateView):
    model = models.Individu
    form_class = forms.IndividuForm


class CoupleCreateView(SuperUserRequiredMixin, CreateView):
    model = models.Couple
    form_class = forms.CoupleForm


class EvenementMixin(SuperUserRequiredMixin):
    fields = ('d', 'm', 'y', 'lieu')

    def get_success_url(self):
        return self.object.inst.get_absolute_url()


class EvenementUpdateView(EvenementMixin, UpdateView):
    pass


class EvenementCreateView(EvenementMixin, CreateView):
    template_name = 'djenealog/evenement_form.html'

    def form_valid(self, form):
        form.instance.inst_id = self.kwargs.get(self.pk_url_kwarg)
        return super().form_valid(form)


class ModelDeleteView(SuperUserRequiredMixin, DeleteView):
    template_name = 'djenealog/confirm_delete.html'
    success_url = '/'


class EvenementDeleteView(ModelDeleteView):
    def get_success_url(self):
        return self.object.inst.get_absolute_url()
