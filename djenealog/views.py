from calendar import LocaleHTMLCalendar
from datetime import date
from subprocess import check_output

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, UpdateView

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from ndh.mixins import SuperUserRequiredMixin

from . import filters, forms, models, tables


# @login_required
def gv(request):
    fmt = request.GET.get("fmt", "html")
    condensed = "condensed" in request.GET
    individus = models.Individu.objects.all()
    couples = models.Couple.objects.all()
    if "famille" in request.GET:
        nom = request.GET["famille"].lower()
        individus = individus.filter(
            Q(nom__icontains=nom)
            | Q(femme__mari__nom__icontains=nom)
            | Q(mari__femme__nom__icontains=nom)
            | Q(parents__mari__nom__icontains=nom)
            | Q(parents__femme__nom__icontains=nom),
        )
        couples = couples.filter(
            Q(mari__nom__icontains=nom) | Q(femme__nom__icontains=nom),
        )
    if "individu" in request.GET:
        individus = set(
            individus.get(pk=int(request.GET["individu"])).family(
                extended="extended" in request.GET,
                upper="upper" in request.GET,
                lower="lower" in request.GET,
            ),
        )
        couples = couples.filter(Q(mari__in=individus) | Q(femme__in=individus))
        for couple in couples:
            if couple.mari:
                individus.add(couple.mari)
            if couple.femme:
                individus.add(couple.femme)
            individus |= set(couple.enfants.all())
    return render(
        request,
        f"djenealog/graph.{fmt}",
        {
            "years": range(
                models.Naissance.objects.exclude(y=None).order_by("y").first().y,
                date.today().year + 1,
            ),
            "individus": individus,
            "couples": couples,
            "condensed": condensed,
        },
    )


# @login_required
@cache_page(60 * 60 * 24)
def img_svg(request):
    individus = models.Individu.objects.all()
    couples = models.Couple.objects.all()
    gv = get_template("djenealog/graph.gv").render(
        {
            "years": range(
                models.Naissance.objects.exclude(y=None).order_by("y").first().y,
                date.today().year + 1,
            ),
            "individus": individus,
            "couples": couples,
        },
    )
    svg = check_output(["dot", "-Tsvg"], input=gv, text=True)
    return HttpResponse(svg, content_type="image/svg+xml")


def stats(request):
    prenom, usage, nom, epouse = (
        {
            row[field]: row["total"]
            for row in models.Individu.objects.all()
            .values(field)
            .annotate(total=Count(field))
            if row[field] != ""
        }
        for field in ("prenom", "usage", "nom", "epouse")
    )

    # merge eg 'Marie-Christine' & 'Marie Christine'
    drop = set()
    for p in prenom.keys():
        if "-" in p and p.replace("-", " ") in prenom.keys():
            prenom[p.replace("-", " ")] += prenom[p]
            drop.add(p)
    prenom = {k: v for k, v in prenom.items() if k not in drop}

    noms, prenoms = set(list(nom.keys()) + list(epouse.keys())), set(
        list(prenom.keys()) + list(usage.keys()),
    )
    noms = [
        (nom.get(n, 0) + epouse.get(n, 0), nom.get(n, 0), epouse.get(n, 0), n)
        for n in noms
        if n != ""
    ]
    prenoms = [
        (prenom.get(n, 0) + usage.get(n, 0), prenom.get(n, 0), usage.get(n, 0), n)
        for n in prenoms
        if n != ""
    ]

    centenaires = models.Individu.objects.filter(
        deces__isnull=True,
        naissance__y__lt=date.today().year - 100,
    )
    maris_pas_masculins = models.Couple.objects.exclude(mari__masculin=True).exclude(
        mari__isnull=True,
    )
    femmes_pas_feminines = models.Couple.objects.exclude(femme__masculin=False).exclude(
        femme__isnull=True,
    )
    divorces_sans_mariages = models.Couple.objects.filter(
        divorce__isnull=False,
        mariage__isnull=True,
    )
    assexues = models.Individu.objects.filter(masculin=None)

    return render(
        request,
        "djenealog/stats.html",
        {
            "individus": models.Individu.objects.count(),
            "couples": models.Couple.objects.count(),
            "naissances": models.Naissance.objects.count(),
            "deces": models.Deces.objects.count(),
            "mariages": models.Mariage.objects.count(),
            "divorces": models.Divorce.objects.count(),
            "pacs": models.Pacs.objects.count(),
            "noms": sorted(noms, reverse=True),
            "prenoms": sorted(prenoms, reverse=True),
            "hommes": models.Individu.objects.filter(masculin=True).count(),
            "femmes": models.Individu.objects.filter(masculin=False).count(),
            "centenaires": centenaires.count(),
            "maris_pas_masculins": maris_pas_masculins.count(),
            "femmes_pas_feminines": femmes_pas_feminines.count(),
            "divorces_sans_mariages": divorces_sans_mariages.count(),
            "assexues": assexues.count(),
        },
    )


@login_required
def annivs(request):
    class AnnivCalendar(LocaleHTMLCalendar):
        cssclass_year = "year table"
        cssclass_month = "month table"

        def __init__(self, annivs, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.annivs = annivs

        def formatday(self, day, weekday):
            if day == 0:
                return '<td class="noday"> </td>'  # day outside month
            annivs = ",<br />".join(
                f"{anniv.symbol} {anniv.inst.get_link()} ({anniv.y})"
                for anniv in self.annivs[(self.current_month, day)]
            )
            return f'<td><span class="font-italic">{day}</span><br />{annivs}</td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            self.current_month = themonth
            return super().formatmonth(theyear, themonth, withyear)

    annivs = {(m, d): [] for m in range(13) for d in range(32)}

    if "individu" in request.GET:
        individus = models.Individu.objects.get(pk=int(request.GET["individu"])).family(
            extended="extended" in request.GET,
            upper="upper" in request.GET,
            lower="lower" in request.GET,
        )
        couples = models.Couple.objects.filter(
            Q(mari__in=individus) | Q(femme__in=individus),
        )
        for couple in couples:
            if couple.mari:
                individus.add(couple.mari)
            if couple.femme:
                individus.add(couple.femme)
            individus |= set(couple.enfants.all())

        for anniv in models.Naissance.objects.filter(
            m__isnull=False,
            d__isnull=False,
            inst__in=individus,
        ).order_by("y"):
            annivs[(anniv.m, anniv.d)].append(anniv)
    else:
        for event in [models.Naissance, models.Mariage, models.Pacs]:
            for anniv in event.objects.filter(
                m__isnull=False,
                d__isnull=False,
            ).order_by("y"):
                annivs[(anniv.m, anniv.d)].append(anniv)

    anniv_cal = AnnivCalendar(annivs).formatyear(date.today().year, 1)
    return render(request, "djenealog/annivs.html", {"anniv_cal": anniv_cal})


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
    fields = ("d", "m", "y", "lieu", "commentaires")
    template_name = "djenealog/evenement_form.html"

    def get_success_url(self):
        return self.object.inst.get_absolute_url()


class EvenementUpdateView(EvenementMixin, UpdateView):
    pass


class EvenementCreateView(EvenementMixin, CreateView):
    def form_valid(self, form):
        form.instance.inst_id = self.kwargs.get(self.pk_url_kwarg)
        return super().form_valid(form)


class ModelDeleteView(SuperUserRequiredMixin, DeleteView):
    template_name = "djenealog/confirm_delete.html"
    success_url = "/"


class EvenementDeleteView(ModelDeleteView):
    def get_success_url(self):
        return self.object.inst.get_absolute_url()
