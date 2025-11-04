from django.urls import path
from . import views

app_name = 'agendamentos'

urlpatterns = [
    # URLs para agendamentos
    path('', views.lista_agendamentos, name='lista_agendamentos'),
    path('criar/', views.criar_agendamento, name='criar_agendamento'),
    path('<str:agendamento_id>/', views.detalhe_agendamento, name='detalhe_agendamento'),
    path('<str:agendamento_id>/cancelar/', views.cancelar_agendamento, name='cancelar_agendamento'),
]