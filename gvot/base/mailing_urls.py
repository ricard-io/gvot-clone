from django.urls import path

from . import views

app_name = 'mailing'
urlpatterns = [
    path('', views.MaillingIndex.as_view(), name='index'),
    path('confirm/', views.MaillingConfirm.as_view(), name='confirm'),
    path('single/<uuid:uuid>/', views.MaillingSingle.as_view(), name='single'),
    path(
        'single_confirm/<uuid:uuid>/',
        views.MaillingSingleConfirm.as_view(),
        name='single_confirm',
    ),
]
