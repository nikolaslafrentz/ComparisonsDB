from django.urls import path
from . import views

app_name = 'stats_comparison'

urlpatterns = [
    path('', views.index, name='index'),
    path('export/', views.export_to_powerbi, name='export_powerbi'),
    path('api/data/', views.powerbi_api, name='powerbi_api'),
]
