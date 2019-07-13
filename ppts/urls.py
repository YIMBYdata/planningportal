from django.urls import path

from ppts import views

urlpatterns = [
    path('', views.index, name='index'),
    path('graphs/<graphname>', views.graphs_manager, name='graph'),
]
