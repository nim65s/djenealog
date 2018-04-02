from django.core.management.base import BaseCommand
import logging

from wikidata.client import Client

from djenealog.models import Individu, Couple, Naissance, Deces

MAX_DIST = 5
client = Client()
logger = logging.getLogger('djenealog.import_wikidata')
done = set()


def get_str(wikidata_id, prop='P1705'):
    obj = client.get(wikidata_id, load=True)
    try:
        return obj.data['claims'][prop][0]['mainsnak']['datavalue']['value']['text']
    except KeyError:
        return obj.description


def get_date(claims, prop):
    return [int(i) for i in claims[prop][0]['mainsnak']['datavalue']['value']['time'][1:11].split('-')]


def get_id(d, num=False):
    ret = d[0]['mainsnak']['datavalue']['value']['id']
    if num:
        return int(ret[1:])
    return ret


def get_individu(wikidata_id, n=1):
    if n > MAX_DIST or wikidata_id in done:
        return
    done.add(wikidata_id)
    obj = client.get(f'Q{wikidata_id}', load=True)
    logger.warning(f'{n}\thttps://www.wikidata.org/wiki/Q{wikidata_id}   \t{obj.description}')
    claims = obj.data['claims']
    family = []

    individu, _ = Individu.objects.get_or_create(wikidata=wikidata_id)
    if individu.prenom or individu.nom:
        return
    # full_name = claims['P1559'][0]['mainsnak']['datavalue']['value']['text']

    if 'P19' in claims and 'datavalue' in claims['P19'][0]['mainsnak']:
        naissance, _ = Naissance.objects.get_or_create(inst=individu)
        naissance.lieu = get_str(get_id(claims['P19']))
        naissance.save()
    if 'P20' in claims and 'datavalue' in claims['P20'][0]['mainsnak']:
        deces, _ = Deces.objects.get_or_create(inst=individu)
        deces.lieu = get_str(get_id(claims['P20']))
        deces.save()
    if 'P21' in claims and 'datavalue' in claims['P21'][0]['mainsnak']:
        individu.masculin = get_id(claims['P21']) == 'Q6581097'
    if 'P734' in claims and 'datavalue' in claims['P734'][0]['mainsnak']:
        individu.nom = get_str(get_id(claims['P734']))
    if 'P735' in claims and 'datavalue' in claims['P735'][0]['mainsnak']:
        individu.prenom = get_str(get_id(claims['P735']))
    if 'P569' in claims and 'datavalue' in claims['P569'][0]['mainsnak']:
        naissance, _ = Naissance.objects.get_or_create(inst=individu)
        naissance.y, naissance.m, naissance.d = get_date(claims, 'P569')
        naissance.save()
    if 'P570' in claims and 'datavalue' in claims['P570'][0]['mainsnak']:
        deces, _ = Deces.objects.get_or_create(inst=individu)
        deces.y, deces.m, deces.d = get_date(claims, 'P570')
        deces.save()

    mari, femme = None, None
    if 'P22' in claims and 'datavalue' in claims['P22'][0]['mainsnak']:
        mari, _ = Individu.objects.get_or_create(wikidata=get_id(claims['P22'], True))
        family.append(get_id(claims['P22'], True))
    if 'P25' in claims and 'datavalue' in claims['P25'][0]['mainsnak']:
        femme, _ = Individu.objects.get_or_create(wikidata=get_id(claims['P25'], True))
        family.append(get_id(claims['P25'], True))
    if mari is not None or femme is not None:
        individu.parents, _ = Couple.objects.get_or_create(mari=mari, femme=femme)
    individu.save()

    if 'P40' in claims:
        for child in claims['P40']:
            family.append(int(child['mainsnak']['datavalue']['value']['id'][1:]))
    if 'P3373' in claims:
        for sibling in claims['P3373']:
            family.append(int(sibling['mainsnak']['datavalue']['value']['id'][1:]))
    for other in set(family):
        get_individu(other, n=n + 1)


class Command(BaseCommand):
    help = 'import a family from wikidata'

    def add_arguments(self, parser):
        parser.add_argument('wikidata_id', type=int)

    def handle(self, wikidata_id, *args, **options):
        get_individu(wikidata_id)
        logger.warning(len(done))
