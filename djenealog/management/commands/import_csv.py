import argparse
import csv
import logging
import re
from enum import IntEnum

from django.core.management.base import BaseCommand

from djenealog import models

STATES = IntEnum("States", "lieu individu couple famille")
mapping = {state: {} for state in STATES}
logger = logging.getLogger("djenealog.import_csv")


def get_or_create_event(cls, inst, ymd, lieu):
    instance, created = cls.objects.get_or_create(inst=inst)
    if lieu and not instance.lieu:
        instance.lieu = mapping[STATES.lieu][lieu]
    y, m, d = (
        int(i) for i in re.match(r"(\d+)?-?(\d+)?-?(\d+)?", ymd).groups(default=0)
    )
    if y and not instance.y:
        instance.y = y
    if m and not instance.m:
        instance.m = m
    if d and not instance.d:
        instance.d = d
    instance.save()


class Command(BaseCommand):
    help = "import a csv file from gramps"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=argparse.FileType("r"))

    def handle(self, csvfile, *args, **options):
        state = STATES.lieu
        jump = 1
        for line in csvfile:
            line = line.strip()
            if jump:
                jump = 0
                logger.debug("-- %s", line)
                continue
            if line == "":
                jump = 1
                state += 1
                logger.debug("-- %s", line)
                continue

            read = next(csv.reader([line]))
            gramps = read[0]

            if state == STATES.lieu:
                mapping[state][gramps] = read[2]

            elif state == STATES.individu:
                nom, prenom, masculin = read[1], read[2], read[7] == "masculin"

                inst, _ = models.Individu.objects.get_or_create(
                    nom=nom,
                    prenom=prenom,
                    masculin=masculin,
                )
                mapping[state][gramps] = inst.pk

                if read[8] or read[9]:
                    get_or_create_event(models.Naissance, inst, read[8], read[9])
                if read[14] or read[15]:
                    get_or_create_event(models.Deces, inst, read[14], read[15])

            elif state == STATES.couple:
                mari = (
                    models.Individu.objects.get(pk=mapping[STATES.individu][read[1]])
                    if read[1]
                    else None
                )
                femme = (
                    models.Individu.objects.get(pk=mapping[STATES.individu][read[2]])
                    if read[2]
                    else None
                )

                inst, _ = models.Couple.objects.get_or_create(mari=mari, femme=femme)
                mapping[state][gramps] = inst.pk

                if read[3] or read[4]:
                    get_or_create_event(models.Mariage, inst, read[3], read[4])

            else:
                enfant = models.Individu.objects.get(
                    pk=mapping[STATES.individu][read[1]],
                )
                enfant.parents = models.Couple.objects.get(
                    pk=mapping[STATES.couple][gramps],
                )
                enfant.save()
