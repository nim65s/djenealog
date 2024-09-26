from typing import ClassVar

from django.forms import ModelForm

from django_select2.forms import Select2Widget

from . import models


class IndividuForm(ModelForm):
    class Meta:
        model = models.Individu
        fields = (
            "prenom",
            "usage",
            "nom",
            "epouse",
            "masculin",
            "parents",
            "commentaires",
        )
        widgets: ClassVar = {
            "parents": Select2Widget,
        }


class CoupleForm(ModelForm):
    class Meta:
        model = models.Couple
        fields = ("mari", "femme", "debut", "fin", "commentaires")
        widgets: ClassVar = {
            "mari": Select2Widget,
            "femme": Select2Widget,
        }
