from django.urls import path

from . import models, views

app_name = 'djenealog'
urlpatterns = [
    path('', views.gv, name='graph'),
    path('stats', views.stats, name='stats'),
    path('individus', views.IndividusView.as_view(), name='individus'),
    path('individu/create', views.IndividuCreateView.as_view(), name='add-individu'),
    path('individu/<int:pk>', views.IndividuView.as_view(), name='individu'),
    path('individu/<int:pk>/delete', views.ModelDeleteView.as_view(model=models.Individu), name='del-individu'),
    path('couples', views.CouplesView.as_view(), name='couples'),
    path('couple/create', views.CoupleCreateView.as_view(), name='add-couple'),
    path('couple/<int:pk>', views.CoupleView.as_view(), name='couple'),
    path('couple/<int:pk>/delete', views.ModelDeleteView.as_view(model=models.Couple), name='del-couple'),
    path('pacs/<int:pk>', views.EvenementUpdateView.as_view(model=models.Pacs), name='pacs'),
    path('pacs/<int:pk>/create', views.EvenementCreateView.as_view(model=models.Pacs), name='add-pacs'),
    path('pacs/<int:pk>/delete', views.EvenementDeleteView.as_view(model=models.Pacs), name='del-pacs'),
    path('mariage/<int:pk>', views.EvenementUpdateView.as_view(model=models.Mariage), name='mariage'),
    path('mariage/<int:pk>/create', views.EvenementCreateView.as_view(model=models.Mariage), name='add-mariage'),
    path('mariage/<int:pk>/delete', views.EvenementDeleteView.as_view(model=models.Mariage), name='del-mariage'),
    path('naissance/<int:pk>', views.EvenementUpdateView.as_view(model=models.Naissance), name='naissance'),
    path('naissance/<int:pk>/create', views.EvenementCreateView.as_view(model=models.Naissance), name='add-naissance'),
    path('naissance/<int:pk>/delete', views.EvenementDeleteView.as_view(model=models.Naissance), name='del-naissance'),
    path('bapteme/<int:pk>', views.EvenementUpdateView.as_view(model=models.Bapteme), name='bapteme'),
    path('bapteme/<int:pk>/create', views.EvenementCreateView.as_view(model=models.Bapteme), name='add-bapteme'),
    path('bapteme/<int:pk>/delete', views.EvenementDeleteView.as_view(model=models.Bapteme), name='del-bapteme'),
    path('deces/<int:pk>', views.EvenementUpdateView.as_view(model=models.Deces), name='deces'),
    path('deces/<int:pk>/create', views.EvenementCreateView.as_view(model=models.Deces), name='add-deces'),
    path('deces/<int:pk>/delete', views.EvenementDeleteView.as_view(model=models.Deces), name='del-deces'),
]
