from django.urls import path

from . import views

app_name = 'import'
urlpatterns = [
    path('', views.ImportIndex.as_view(), name='index'),
    path('confirm/', views.ImportConfirm.as_view(), name='confirm'),
]
