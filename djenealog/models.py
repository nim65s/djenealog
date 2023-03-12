import calendar
import time
from datetime import date, datetime, timedelta

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db.models import Q
from django.urls import reverse

from ndh.models import Links, NamedModel
from wikidata.client import Client


def timestamp(event):
    return datetime(*event.date().timetuple()[:-2]).timestamp()


def mean_date(qs):
    return date.fromtimestamp(
        sum([time.mktime(q.date().timetuple()) for q in qs]) / qs.count(),
    )


class Individu(models.Model, Links):
    nom = models.CharField(max_length=50, blank=True)
    prenom = models.CharField("Prénom", max_length=50, blank=True)
    usage = models.CharField("Prénom d`usage", max_length=50, blank=True)
    epouse = models.CharField("Nom d`épouse ou d`usage", max_length=50, blank=True)
    masculin = models.BooleanField(null=True)
    parents = models.ForeignKey(
        "Couple",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="enfants",
    )
    wikidata = models.PositiveIntegerField(blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True)

    def __str__(self):
        psep = " / " if self.prenom and self.usage else " "
        nsep = " / " if self.nom and self.epouse else " "
        return f"{self.prenom}{psep}{self.usage} {self.nom}{nsep}{self.epouse}".strip()

    def label(self):
        naissance = (
            self.naissance if Naissance.objects.filter(inst=self).exists() else ""
        )
        deces = self.deces if Deces.objects.filter(inst=self).exists() else ""
        return f"{self}\n{naissance}\n{deces}\n".replace("  ", " ")

    def color(self):
        return "e0e0ff" if self.masculin else "ffffe0"

    def node(self):
        ret = ["{"]
        rank = self.rank()
        if rank:
            ret.append(f"rank=same; {rank};")
        ret.append(
            f'"I{self.pk}" [fillcolor="#{self.color()}" label="{self.label()}" '
            f'URL="{self.get_absolute_url()}"',
        )
        ret.append('shape="box"];')
        return "\n".join([*ret, "}"])

    def conjoints(self):
        return Individu.objects.filter(Q(femme__mari=self) | Q(mari__femme=self))

    def start(self):
        if Naissance.objects.filter(y__isnull=False, inst=self).exists():
            return self.naissance.date()
        conjoints = Naissance.objects.filter(y__isnull=False, inst__in=self.conjoints())
        if conjoints.exists():
            return conjoints.order_by("y").last().date()
        siblings = Naissance.objects.filter(
            y__isnull=False,
            inst__parents=self.parents,
        ).order_by("y")
        if self.parents and siblings.exists():
            return date.fromtimestamp(
                (timestamp(siblings.first()) + timestamp(siblings.last())) / 2,
            )
        enfants = Naissance.objects.filter(
            Q(inst__parents__femme=self) | Q(inst__parents__mari=self),
            y__isnull=False,
        )
        if enfants.exists():
            return enfants.order_by("y").first().date() - timedelta(days=20 * 365)
        parents = Naissance.objects.filter(
            Q(inst__femme__enfants=self) | Q(inst__mari__enfants=self),
            y__isnull=False,
        )
        if parents.exists():
            parents = parents.order_by("y")
            mid = date.fromtimestamp(
                (timestamp(parents.first()) + timestamp(parents.last())) / 2,
            )
            return mid + timedelta(days=20 * 365)
        return None

    def rank(self):
        start = self.start()
        if start:
            return start.year
        return None

    def y(self):
        start = self.start()
        if start:
            return -(start.year + (start.month + start.day / 30) / 12)
        return None

    def ancestors(self):
        """Return a set of ancestors."""
        ancestors = set()
        if self.parents:
            if self.parents.mari:
                ancestors.add(self.parents.mari)
                ancestors |= self.parents.mari.ancestors()
            if self.parents.femme:
                ancestors.add(self.parents.femme)
                ancestors |= self.parents.femme.ancestors()
        return ancestors

    def descendants(self):
        """Return a set of descendants."""
        descendants = set()
        for couple in self.femme.all():
            for enfant in couple.enfants.all():
                descendants.add(enfant)
                descendants |= enfant.descendants()
        for couple in self.mari.all():
            for enfant in couple.enfants.all():
                descendants.add(enfant)
                descendants |= enfant.descendants()
        return descendants

    def family(self, extended=False, upper=True, lower=True):
        """Return a set of all descendant ancestors and ancestor descendants."""
        family = {self} | set(self.conjoints())
        if upper:
            for ancestor in self.ancestors():
                family.add(ancestor)
                if extended:
                    family |= ancestor.descendants()
        if lower:
            for descendant in self.descendants():
                family.add(descendant)
                if extended:
                    family |= descendant.ancestors()
        return family


class Couple(models.Model, Links):
    mari = models.ForeignKey(
        Individu,
        on_delete=models.PROTECT,
        related_name="mari",
        blank=True,
        null=True,
    )
    femme = models.ForeignKey(
        Individu,
        on_delete=models.PROTECT,
        related_name="femme",
        blank=True,
        null=True,
    )
    debut = models.DateField(blank=True, null=True)
    fin = models.DateField(blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True)

    def __str__(self):
        mari, femme = self.mari or "", self.femme or ""
        return f"{femme} & {mari}".replace("  ", " ")

    def label(self):
        ret = []
        if Pacs.objects.filter(inst=self).exists():
            ret.append(self.pacs)
        if Mariage.objects.filter(inst=self).exists():
            ret.append(self.mariage)
        if Divorce.objects.filter(inst=self).exists():
            ret.append(self.divorce)
        return "\n".join(str(r).strip() for r in ret)

    def color(self):
        if Divorce.objects.filter(inst=self).exists():
            return "ffe0e0"
        if Mariage.objects.filter(inst=self).exists():
            return "e0ffe0"
        if Pacs.objects.filter(inst=self).exists():
            return "ffe0ff"
        return "e0ffff"

    def node(self):
        ret = ["{"]
        rank = self.rank()
        if rank:
            ret.append(f"rank=same; {rank};")
        ret.append(
            f'"F{self.pk}" [label="{self.label()}" URL="{self.get_absolute_url()}" ',
        )
        ret.append(f'shape="ellipse" fillcolor="#{self.color()}"];')
        ret.append("}")
        ret.append(f"subgraph cluster_parents_F{self.pk}")
        ret.append('{ style="invis";')
        if self.mari:
            ret.append(f'"I{self.mari.pk}" -> "F{self.pk}" ;')
        if self.femme:
            ret.append(f'"I{self.femme.pk}" -> "F{self.pk}" ;')
        ret.append("}")
        ret.append(f"subgraph cluster_enfants_f{self.pk}")
        ret.append('{ style="invis";')
        for enfant in self.enfants.all():
            ret.append(f'"F{self.pk}" -> "I{enfant.pk}" ;')
        ret.append("}")
        return "\n".join(ret)

    def start(self):
        if self.debut:
            return self.debut
        pacs = Pacs.objects.filter(y__isnull=False, inst=self)
        mariage = Mariage.objects.filter(y__isnull=False, inst=self)
        if pacs.exists() or mariage.exists():
            start = self.pacs.date() if pacs.exists() else self.mariage.date()
            # avoid upward arrows, as child can be born before wedding.
            first = (
                self.enfants.filter(naissance__y__lt=start.year + 2)
                .order_by("naissance__y")
                .first()
            )
            if first:
                start = first.naissance.date() - timedelta(days=2 * 365)
            return start
        naissances = Naissance.objects.filter(
            y__isnull=False,
            inst__in=[self.mari, self.femme],
        )
        if naissances.exists():
            return naissances.order_by("y").last().date() + timedelta(days=15 * 365)
        return None

    def rank(self):
        start = self.start()
        if start:
            return start.year
        return None

    def y(self):
        start = self.start()
        if start:
            return -(start.year + (start.month + start.day / 30) / 12)
        return None


class Lieu(Links, NamedModel):
    wikidata = models.PositiveIntegerField(blank=True, null=True)

    point = models.PointField(geography=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Lieux"
        ordering = ["name"]

    @property
    def wikidata_url(self):
        return f"https://www.wikidata.org/wiki/Q{self.wikidata}"

    def save(self, *args, **kwargs):
        if self.wikidata:
            claims = Client().get(f"Q{self.wikidata}", load=True).data["claims"]

            self.name = claims["P373"][0]["mainsnak"]["datavalue"]["value"]
            coordinate = claims["P625"][0]["mainsnak"]["datavalue"]["value"]
            self.point = Point(coordinate["longitude"], coordinate["latitude"])
        return super().save(*args, **kwargs)


class Evenement(models.Model):
    lieu = models.ForeignKey(Lieu, blank=True, null=True, on_delete=models.PROTECT)
    y = models.PositiveSmallIntegerField("année", blank=True, null=True)
    m = models.PositiveSmallIntegerField("mois", blank=True, null=True)
    d = models.PositiveSmallIntegerField("jour", blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True)
    symbol = ""

    class Meta:
        abstract = True

    def __str__(self):
        ret = []
        d, m, y = (
            self.d or "",
            calendar.month_name[self.m].lower() if self.m else "",
            self.y or "",
        )
        ret.append(f"{d} {m} {y}".strip())
        ret.append("" if self.lieu is None else str(self.lieu))
        return (self.symbol + " " + ", ".join(r for r in ret if r)).strip()

    def get_absolute_url(self):
        app, model = self._meta.app_label, self._meta.model_name
        return reverse(f"{app}:{model}", kwargs={"pk": self.inst.pk})

    def date(self):
        if self.y:
            return date(self.y, self.m or 1, self.d or 1)
        return None


class Naissance(Evenement):
    inst = models.OneToOneField(Individu, on_delete=models.PROTECT)
    symbol = "*"


class Deces(Evenement):
    inst = models.OneToOneField(Individu, on_delete=models.PROTECT)
    symbol = "✝"

    class Meta:
        verbose_name = "décès"
        verbose_name_plural = "décès"


class Pacs(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)
    symbol = "P"

    class Meta:
        verbose_name_plural = "pacs"


class Mariage(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)
    symbol = "⚭"


class Divorce(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)
    symbol = "⚮"
