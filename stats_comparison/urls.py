from django.urls import path
from . import views

app_name = 'stats_comparison'

urlpatterns = [
    path('', views.index, name='index'),
]
