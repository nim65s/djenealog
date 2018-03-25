import argparse
import csv
from enum import IntEnum

from django.core.management.base import BaseCommand

from djenealog.models import Lieu, Individu, Couple, new_gramps, strpdate, parse_gramps


STATES = IntEnum('States', 'lieu individu couple famille')
mapping = {state: {} for state in STATES}

class Command(BaseCommand):
    help = 'import a csv file from gramps'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=argparse.FileType('r'))

    def handle(self, csvfile, *args, **options):
        state = STATES.lieu
        jump = 1
        for line in csvfile:
            line = line.strip()
            if jump:
                jump = 0
                print(f'-- {line}')
                continue
            if line == '':
                jump = 1
                state += 1
                print(f'-- {line}')
                continue

            read = next(csv.reader([line]))
            gramps = parse_gramps(read[0])

            if state == STATES.lieu:
                nom = read[2]

                inst, _ = Lieu.objects.get_or_create(nom=nom, defaults={'gramps': new_gramps(Lieu, gramps)})
                mapping[state][gramps] = inst.gramps

            elif state == STATES.individu:
                nom, prenom, masculin = read[1], read[2], read[7] == 'masculin'
                naissance_ymd, naissance, deces_ymd, deces = strpdate(read[8]), read[9], strpdate(read[14]), read[15]

                defaults = {
                    'gramps': new_gramps(Individu, gramps),
                    'naissance_y': naissance_ymd[0], 'naissance_m': naissance_ymd[1], 'naissance_d': naissance_ymd[2],
                    'deces_y': deces_ymd[0], 'deces_m': deces_ymd[1], 'deces_d': deces_ymd[2],
                }
                if naissance:
                    defaults['naissance'] = Lieu.objects.get(gramps=mapping[STATES.lieu][parse_gramps(naissance)])
                if deces:
                    defaults['deces'] = Lieu.objects.get(gramps=mapping[STATES.lieu][parse_gramps(deces)])

                inst, _ = Individu.objects.get_or_create(nom=nom, prenom=prenom, masculin=masculin, defaults=defaults)
                mapping[state][gramps] = inst.gramps

            elif state == STATES.couple:
                mari, femme = (Individu.objects.get(gramps=mapping[STATES.individu][parse_gramps(read[i])])
                               for i in (1, 2))
                mariage_ymd, mariage = strpdate(read[3]), read[4]

                defaults = {
                    'gramps': new_gramps(Couple, gramps),
                    'mariage_y': mariage_ymd[0], 'mariage_m': mariage_ymd[1], 'mariage_d': mariage_ymd[2],
                }
                if mariage:
                    defaults['mariage'] = Lieu.objects.get(gramps=mapping[STATES.lieu][parse_gramps(mariage)])

                inst, _ = Couple.objects.get_or_create(mari=mari, femme=femme, defaults=defaults)
                mapping[state][gramps] = inst.gramps

            else:
                 enfant = Individu.objects.get(gramps=mapping[STATES.individu][parse_gramps(read[1])])
                 enfant.parents = Couple.objects.get(gramps=mapping[STATES.couple][gramps])
                 enfant.save()
