from django.urls import path

from ppts import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.getimage, name='testgraph'),
]
