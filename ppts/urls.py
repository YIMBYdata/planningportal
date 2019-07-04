from django.urls import path

from ppts import views

urlpatterns = [
    path('', views.index, name='index'),
    path('graphs/samplegraph', views.samplegraph, name='sample graph'),
]
