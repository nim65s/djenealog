import logging
from collections import deque
from datetime import date

from django.db.models import Q

from . import models

logger = logging.getLogger('djenealog.svg')

IDX = (4, 6, 13, 25, 26, 28, 30, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 54, 56, 59, 61, 63, 67, 86, 95, 96,
       97, 103, 118, 119, 120, 121, 122, 123, 125, 130, 131, 132, 133, 134, 135, 153, 227, 346, 475, 476, 486)


def dt_px(dt, start=1925):
    """Get the number of days from start to dt."""
    return (dt - date(start, 1, 1)).days


def end_individu(inst, start=1925):
    """Get the last day of an individu."""
    qs = models.Deces.objects.filter(inst=inst)
    return dt_px(qs.first().date() if qs.exists() else date.today(), start)


def end_couple(inst, start=1925):
    """Get the last day of a couple."""
    if inst.fin is not None:
        return dt_px(inst.fin, start)
    qs = models.Divorce.objects.filter(inst=inst)
    if qs:
        return dt_px(qs.first().date(), start)
    return min(end_individu(inst.mari), end_individu(inst.femme))


def tree(individus, couples, first):
    """Sort all individus and couples in a family tree."""
    ret = [first]
    added = deque()

    def insert(index, individu):
        if individu in ret or individu not in individus:
            print(f'skipping insertion of {individu}')
        else:
            print(f'inserting {individu}')
            ret.insert(index, individu)
            added.appendleft(individu)

    def process(individu):
        print(f'processing {individu} conjoints')
        for conjoint in individu.conjoints():
            insert(ret.index(individu) + 1 if conjoint.masculin else -1, conjoint)

        print(f'processing {individu} children')
        enfants = Q(inst__parents__femme=individu) | Q(inst__parents__mari=individu)
        for enfant in models.Naissance.objects.filter(enfants).order_by('y', 'm', 'd'):
            if enfant.inst.masculin:
                if enfant.inst.parents.femme in individus:
                    insert(ret.index(enfant.inst.parents.femme), enfant.inst)
                else:
                    insert(ret.index(enfant.inst.parents.mari), enfant.inst)
            else:
                if enfant.inst.parents.mari in individus:
                    insert(ret.index(enfant.inst.parents.mari) + 1, enfant.inst)
                else:
                    insert(ret.index(enfant.inst.parents.femme) + 1, enfant.inst)

        print(f'processing {individu} parents')
        if individu.parents:
            if individu.masculin:
                if individu.parents.femme:
                    insert(len(ret) + 1, individu.parents.femme)
                if individu.parents.mari and individu.parents.mari in individus:
                    insert(len(ret) + 1, individu.parents.mari)
            else:
                if individu.parents.mari:
                    insert(0, individu.parents.mari)
                if individu.parents.femme:
                    insert(0, individu.parents.femme)
        print(ret)

    process(first)
    while True:
        try:
            process(added.pop())
        except IndexError:
            break

    return ret


def svg():
    individus = models.Individu.objects.filter(pk__in=IDX)
    couples = models.Couple.objects.filter(mari__in=IDX, femme__in=IDX)
    start = sorted(i.start() for i in individus)[0].year
    width = dt_px(date.today(), start)

    individus = tree(individus, couples, models.Individu.objects.get(prenom='Émilia'))

    individus = [(i, dt_px(i.start(), start), end_individu(i, start)) for i in individus]
    couples = [(c, dt_px(c.start(), start), end_couple(c, start)) for c in couples]

    for i, s, e in individus:
        logger.info(f'{i} {s} - {e}')
    for c, s, e in couples:
        logger.info(f'{c} {s} - {e}')

    individus = [(i, s, e - s) for i, s, e in individus]
    couples = [(c, s, e - s) for c, s, e in couples]

    return (individus, couples, width)
