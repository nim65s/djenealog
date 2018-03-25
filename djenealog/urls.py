from django.urls import path

from . import views

app_name = 'djenealog'
urlpatterns = [
    path('', views.gv, name='graph'),
    path('individus', views.IndividusView.as_view(), name='individus'),
    path('couples', views.CouplesView.as_view(), name='couples'),
]
