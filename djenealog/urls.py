from django.urls import path

from . import views

app_name = 'djenealog'
urlpatterns = [
    path('', views.gv, name='graph'),
    path('individus', views.IndividusView.as_view(), name='individus'),
    path('individu/<int:pk>', views.IndividuView.as_view(), name='individu'),
    path('couples', views.CouplesView.as_view(), name='couples'),
    path('couple/<int:pk>', views.CoupleView.as_view(), name='couple'),
]
