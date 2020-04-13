from django.urls import path

from . import views

app_name = 'mailling'
urlpatterns = [
    path('', views.MaillingIndex.as_view(), name='index'),
    path('confirm/', views.MaillingConfirm.as_view(), name='confirm'),
]
