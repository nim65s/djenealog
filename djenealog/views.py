from datetime import date
from django.shortcuts import render
from django.views.generic import UpdateView, CreateView, DeleteView

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from . import models, tables, filters, forms


def gv(request):
    fmt = request.GET.get('fmt', 'html')
    return render(request, f'djenealog/graph.{fmt}', {
        'years': range(models.Naissance.objects.exclude(y=None).order_by('y').first().y, date.today().year + 1),
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
    form_class = forms.IndividuForm


class CoupleView(UpdateView):
    model = models.Couple
    form_class = forms.CoupleForm


class IndividuCreateView(CreateView):
    model = models.Individu
    form_class = forms.IndividuForm


class CoupleCreateView(CreateView):
    model = models.Couple
    form_class = forms.CoupleForm


class EvenementMixin(object):
    fields = ('lieu', 'y', 'm', 'd')

    def get_success_url(self):
        return self.object.inst.get_absolute_url()


class EvenementUpdateView(EvenementMixin, UpdateView):
    pass


class EvenementCreateView(EvenementMixin, CreateView):
    def form_valid(self, form):
        form.instance.inst_id = self.kwargs.get(self.pk_url_kwarg)
        return super().form_valid(form)


class ModelDeleteView(DeleteView):
    template_name = 'djenealog/confirm_delete.html'
    success_url = '/'


class EvenementDeleteView(ModelDeleteView):
    def get_success_url(self):
        return self.object.inst.get_absolute_url()
