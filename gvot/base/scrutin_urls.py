from django.urls import path

from . import views

app_name = 'scrutin'
urlpatterns = [
    path('add/', views.ScrutinAdd.as_view(), name='add'),
]
