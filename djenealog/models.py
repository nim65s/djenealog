import re
from enum import IntEnum
from django.db import models
from django.urls import reverse

from ndh.utils import enum_to_choices
from ndh.models import Links


class Individu(models.Model, Links):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    masculin = models.NullBooleanField()
    parents = models.ForeignKey('Couple', on_delete=models.PROTECT, blank=True, null=True, related_name='enfants')

    def __str__(self):
        return f'{self.prenom} {self.nom}'

    def label(self):
        naissance = self.naissance if Naissance.objects.filter(inst=self).exists() else ''
        deces = self.deces if Deces.objects.filter(inst=self).exists() else ''
        return f'{self}\n{naissance}\n{deces}'

    def node(self):
        ret = ['{']
        if Naissance.objects.filter(inst=self).exists() and self.naissance.y:
            ret.append(f'rank=same; {self.naissance.y};')
        color = 'e0e0ff' if self.masculin else 'ffffe0'
        ret.append(f'"I{self.pk}" [ fillcolor="#{color}" label="{self.label()}" URL="{self.get_absolute_url()}"')
        ret.append('shape="box" style="solid,filled" ];')
        return '\n'.join(ret + ['}'])


class Couple(models.Model, Links):
    mari = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='pere', blank=True, null=True)
    femme = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='mere', blank=True, null=True)

    def __str__(self):
        return f'{self.femme} & {self.mari}'

    def label(self):
        return self.mariage if Mariage.objects.filter(inst=self).exists() else ''

    def node(self):
        ret = [f'"F{self.pk}" [ label="{self.label()}" URL="{self.get_absolute_url()}" ']
        ret.append('shape="ellipse" fillcolor="#ffffe0" style="filled" ];')
        ret.append(f'subgraph cluster_F{self.pk}')
        ret.append('{ style="invis";')
        if self.mari:
            ret.append(f'"I{self.mari.pk}" -> "F{self.pk}" [arrowhead=normal arrowtail=none dir=both ];')
        if self.femme:
            ret.append(f'"I{self.femme.pk}" -> "F{self.pk}" [arrowhead=normal arrowtail=none dir=both ];')
        return '\n'.join(ret + ['}'])


class Evenement(models.Model):
    lieu = models.CharField(max_length=50, blank=True, null=True)
    y = models.PositiveSmallIntegerField('année', blank=True, null=True)
    m = models.PositiveSmallIntegerField('mois', blank=True, null=True)
    d = models.PositiveSmallIntegerField('jour', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        ret = ''
        if self.y:
            ret += f'{self.y}'
            if self.m:
                ret += f'-{self.m}'
                if self.d:
                    ret += f'-{self.d}'
        if ret and self.lieu:
            ret += ', '
        if self.lieu:
            ret += f'{self.lieu}'
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


class Pacs(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)


class Mariage(Evenement):
    inst = models.OneToOneField(Couple, on_delete=models.PROTECT)
