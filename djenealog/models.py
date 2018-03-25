import re
from django.db import models


class Lieu(models.Model):
    gramps = models.PositiveSmallIntegerField(unique=True)
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class Individu(models.Model):
    gramps = models.PositiveSmallIntegerField(unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    masculin = models.NullBooleanField()
    naissance = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name='+', null=True)
    naissance_y = models.PositiveSmallIntegerField()
    naissance_m = models.PositiveSmallIntegerField()
    naissance_d = models.PositiveSmallIntegerField()
    deces = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name='+', null=True)
    deces_y = models.PositiveSmallIntegerField()
    deces_m = models.PositiveSmallIntegerField()
    deces_d = models.PositiveSmallIntegerField()
    parents = models.ForeignKey('Couple', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.prenom} {self.nom}'


class Couple(models.Model):
    gramps = models.PositiveSmallIntegerField(unique=True)
    mari = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='pere')
    femme = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='mere')
    mariage = models.ForeignKey(Lieu, on_delete=models.PROTECT, null=True)
    mariage_y = models.PositiveSmallIntegerField()
    mariage_m = models.PositiveSmallIntegerField()
    mariage_d = models.PositiveSmallIntegerField()
    pacs = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.femme} & {self.mari}'


def new_gramps(cls, default=None):
    if default is not None and not cls.objects.filter(gramps=default).exists():
        return default
    return cls.objects.order_by('-gramps').first().gramps + 1


def strpdate(date):
    """
    '', 'YYYY', 'YYYY-MM, 'YYYY-MM-DD' -> (YYYY || 0, MM || 0, DD || 0)
    """
    return [int(i) for i in re.match(r'(\d+)?-?(\d+)?-?(\d+)?', date).groups(default=0)]


def parse_gramps(gramps):
    """
    '[F0040]' -> 40
    """
    return int(gramps[2:-1])
