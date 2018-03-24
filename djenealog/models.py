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
    naissance = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name='+')
    naissance_y = models.PositiveSmallIntegerField()
    naissance_m = models.PositiveSmallIntegerField()
    naissance_d = models.PositiveSmallIntegerField()
    deces = models.ForeignKey(Lieu, on_delete=models.PROTECT, related_name='+')
    deces_y = models.PositiveSmallIntegerField()
    deces_m = models.PositiveSmallIntegerField()
    deces_d = models.PositiveSmallIntegerField()
    famille = models.ForeignKey('Famille', on_delete=models.PROTECT)


class Famille(models.Model):
    gramps = models.PositiveSmallIntegerField(unique=True)
    mari = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='pere')
    femme = models.ForeignKey(Individu, on_delete=models.PROTECT, related_name='mere')
    mariage = models.ForeignKey(Lieu, on_delete=models.PROTECT)
    mariage_y = models.PositiveSmallIntegerField()
    mariage_m = models.PositiveSmallIntegerField()
    mariage_d = models.PositiveSmallIntegerField()
    pacs = models.BooleanField(default=False)
