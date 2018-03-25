from django.urls import path

from . import views

app_name = 'djenealog'
urlpatterns = [
    path('', views.gv, name='graph'),
]
