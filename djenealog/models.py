import calendar

from django.db import models
from django.db.models import Q
from django.urls import reverse

from ndh.models import Links


class Individu(models.Model, Links):
    nom = models.CharField(max_length=50, blank=True)
    prenom = models.CharField('Prénom', max_length=50, blank=True)
    usage = models.CharField('Prénom d’usage', max_length=50, blank=True)
    epouse = models.CharField('Nom d’épouse ou d’usage', max_length=50, blank=True)
    masculin = models.NullBooleanField()
    parents = models.ForeignKey('Couple', on_delete=models.PROTECT, blank=True, null=True, related_name='enfants')

    def __str__(self):
        psep = ' / ' if self.prenom and self.usage else ' '
        nsep = ' / ' if self.nom and self.epouse else ' '
        return f'{self.prenom}{psep}{self.usage} {self.nom}{nsep}{self.epouse}'.strip()

    def label(self):
        naissance = self.naissance if Naissance.objects.filter(inst=self).exists() else ''
        deces = self.deces if Deces.objects.filter(inst=self).exists() else ''
        return f'{self}\n{naissance}\n{deces}\n'

    def node(self):
        ret = ['{']
        rank = self.rank()
        if rank:
            ret.append(f'rank=same; {rank};')
        color = 'e0e0ff' if self.masculin else 'ffffe0'
        ret.append(f'"I{self.pk}" [ fillcolor="#{color}" label="{self.label()}" URL="{self.get_absolute_url()}"')
        ret.append('shape="box" style="solid,filled" ];')
        return '\n'.join(ret + ['}'])

    def conjoints(self):
        return Individu.objects.filter((Q(femme__mari=self) | Q(mari__femme=self)))

    def rank(self):
        if Naissance.objects.filter(y__isnull=False, inst=self).exists():
            return self.naissance.y
        conjoints = Naissance.objects.filter(y__isnull=False, inst__in=self.conjoints())
        if conjoints.exists():
            return conjoints.order_by('y').last().y
        siblings = Naissance.objects.filter(y__isnull=False, inst__parents=self.parents).order_by('y')
        if self.parents and siblings.exists():
            return (siblings.first().y + siblings.last().y) // 2
        enfants = Naissance.objects.filter(Q(inst__parents__femme=self) | Q(inst__parents__mari=self), y__isnull=False)
        if enfants.exists():
            return enfants.order_by('y').first().y - 20
        parents = Naissance.objects.filter(Q(inst__femme__enfants=self) | Q(inst__mari__enfants=self), y__isnull=False)
        if parents.exists():
            parents = parents.order_by('y')
            return (parents.first().y + parents.last().y) // 2 + 20


class Couple(models.Model, Links):
    mari = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='mari', blank=True, null=True)
    femme = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='femme', blank=True, null=True)

    def __str__(self):
        mari, femme = self.mari or '', self.femme or ''
        return f'{femme} & {mari}'

    def label(self):
        return self.mariage if Mariage.objects.filter(inst=self).exists() else ''

    def node(self):
        ret = ['{']
        rank = self.rank()
        if rank:
            ret.append(f'rank=same; {rank};')
        ret.append(f'"F{self.pk}" [ label="{self.label()}" URL="{self.get_absolute_url()}" ')
        ret.append('shape="ellipse" fillcolor="#ffffe0" style="filled" ];')
        ret.append('}')
        ret.append(f'subgraph cluster_parents_F{self.pk}')
        ret.append('{ style="invis";')
        if self.mari:
            ret.append(f'"I{self.mari.pk}" -> "F{self.pk}" [arrowhead=normal arrowtail=none dir=both ];')
        if self.femme:
            ret.append(f'"I{self.femme.pk}" -> "F{self.pk}" [arrowhead=normal arrowtail=none dir=both ];')
        ret.append('}')
        ret.append(f'subgraph cluster_enfants_f{self.pk}')
        ret.append('{ style="invis";')
        for enfant in self.enfants.all():
            ret.append(f'"F{self.pk}" -> "I{enfant.pk}" [ arrowhead=normal arrowtail=none dir=both ];')
        ret.append('}')
        return '\n'.join(ret)

    def rank(self):
        # if Mariage.objects.filter(y__isnull=False, inst=self).exists():
            # return self.mariage.y
        naissances = Naissance.objects.filter(y__isnull=False, inst__in=[self.mari, self.femme])
        if naissances.exists():
            return naissances.order_by('y').last().y + 15


class Evenement(models.Model):
    lieu = models.CharField(max_length=50, blank=True, null=True)
    y = models.PositiveSmallIntegerField('année', blank=True, null=True)
    m = models.PositiveSmallIntegerField('mois', blank=True, null=True)
    d = models.PositiveSmallIntegerField('jour', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        d, m, y = self.d or '', calendar.month_name[self.m] if self.m else '', self.y or ''
        ret = f'{d} {m} {y}'
        if self.lieu:
            ret += f', {self.lieu}'
        return ret

    def get_absolute_url(self):
        app, model = self._meta.app_label, self._meta.model_name
        return reverse(f'{app}:{model}', kwargs={'pk': self.inst.pk})


class Naissance(Evenement):
    inst = models.OneToOneField(Individu, on_delete=models.PROTECT)


class Bapteme(Evenement):
    inst = models.OneToOneField(Individu, on_delete=models.PROTECT)


class Deces(Evenement):
    inst = models.OneToOneField(Individu, on_delete=models.PROTECT)

    def __str__(self):
        ret = super().__str__()
        if ret.strip():
            return ret
        return '✝'


class Pacs(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)


class Mariage(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)


class Divorce(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)
