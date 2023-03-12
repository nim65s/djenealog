import logging

from django.core.management.base import BaseCommand

from wikidata.client import Client

from djenealog.models import Couple, Deces, Individu, Lieu, Naissance

logger = logging.getLogger("djenealog.import_wikidata")


class WikiData:
    def __init__(self, wikidata_id, max_dist=5, logger=None):
        self.client = Client()
        self.done = set()
        self.logger = logger
        self.max_dist = max_dist
        self.get_individu(wikidata_id)
        logger.warning(len(self.done))

    def get_id(self, claim):
        return claim["mainsnak"]["datavalue"]["value"]["numeric-id"]

    def get_str(self, claim, prop="P1705"):
        wikidata_id = self.get_id(claim)
        obj = self.client.get(f"Q{wikidata_id}", load=True)
        try:
            return obj.data["claims"][prop][0]["mainsnak"]["datavalue"]["value"]["text"]
        except KeyError:
            return obj.description

    def get_date(self, claim):
        return [
            int(i)
            for i in claim["mainsnak"]["datavalue"]["value"]["time"][1:11].split("-")
        ]

    def get_lieu(self, claim):
        wikidata_id = self.get_id(claim)
        lieu, _ = Lieu.objects.get_or_create(wikidata=wikidata_id)
        return lieu

    def get_individu(self, wikidata_id, n=1):
        if n > self.max_dist or wikidata_id in self.done:
            return
        self.done.add(wikidata_id)
        obj = self.client.get(f"Q{wikidata_id}", load=True)
        self.logger.warning(
            "%s\thttps://www.wikidata.org/wiki/Q%s   \t%s",
            n,
            wikidata_id,
            obj.description,
        )
        claims = obj.data["claims"]
        family = []

        individu, _ = Individu.objects.get_or_create(wikidata=wikidata_id)
        if individu.prenom or individu.nom:
            return
        # full_name = claims['P1559'][0]['mainsnak']['datavalue']['value']['text']

        if "P19" in claims and "datavalue" in claims["P19"][0]["mainsnak"]:
            naissance, _ = Naissance.objects.get_or_create(inst=individu)
            naissance.lieu = self.get_lieu(claims["P19"][0])
            naissance.save()
        if "P20" in claims and "datavalue" in claims["P20"][0]["mainsnak"]:
            deces, _ = Deces.objects.get_or_create(inst=individu)
            deces.lieu = self.get_lieu(claims["P20"][0])
            deces.save()
        if "P21" in claims and "datavalue" in claims["P21"][0]["mainsnak"]:
            individu.masculin = self.get_id(claims["P21"][0]) == 6581097
        if "P734" in claims and "datavalue" in claims["P734"][0]["mainsnak"]:
            individu.nom = self.get_str(claims["P734"][0])
        if "P735" in claims and "datavalue" in claims["P735"][0]["mainsnak"]:
            individu.prenom = self.get_str(claims["P735"][0])
        if "P569" in claims and "datavalue" in claims["P569"][0]["mainsnak"]:
            naissance, _ = Naissance.objects.get_or_create(inst=individu)
            naissance.y, naissance.m, naissance.d = self.get_date(claims["P569"][0])
            naissance.save()
        if "P570" in claims and "datavalue" in claims["P570"][0]["mainsnak"]:
            deces, _ = Deces.objects.get_or_create(inst=individu)
            deces.y, deces.m, deces.d = self.get_date(claims["P570"][0])
            deces.save()

        mari, femme = None, None
        if "P22" in claims and "datavalue" in claims["P22"][0]["mainsnak"]:
            mari, _ = Individu.objects.get_or_create(
                wikidata=self.get_id(claims["P22"][0]),
            )
            family.append(self.get_id(claims["P22"][0]))
        if "P25" in claims and "datavalue" in claims["P25"][0]["mainsnak"]:
            femme, _ = Individu.objects.get_or_create(
                wikidata=self.get_id(claims["P25"][0]),
            )
            family.append(self.get_id(claims["P25"][0]))
        if mari is not None or femme is not None:
            individu.parents, _ = Couple.objects.get_or_create(mari=mari, femme=femme)
        individu.save()

        if "P40" in claims:
            for child in claims["P40"]:
                family.append(self.get_id(child))
        if "P3373" in claims:
            for sibling in claims["P3373"]:
                family.append(self.get_id(sibling))
        for other in set(family):
            self.get_individu(other, n=n + 1)


class Command(BaseCommand):
    help = "import a family from wikidata"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument("wikidata_id", type=int)
        parser.add_argument("--max_dist", type=int, default=5)

    def handle(self, wikidata_id, max_dist, *args, **options):
        WikiData(wikidata_id, max_dist=max_dist, logger=logger)
