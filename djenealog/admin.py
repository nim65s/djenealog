from django.contrib import admin

from . import models

admin.site.register(models.Individu)
admin.site.register(models.Couple)
admin.site.register(models.Naissance)
admin.site.register(models.Deces)
admin.site.register(models.Pacs)
admin.site.register(models.Mariage)
admin.site.register(models.Divorce)
