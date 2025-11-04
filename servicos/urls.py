from django.urls import path
from . import views
from . import admin_views
from . import roupas_views
from . import vestuario_views
from django.contrib.auth import views as auth_views

app_name = 'servicos'

# Define as rotas/URLs da aplicação
urlpatterns = [
    # Página principal dos serviços
    path('', views.lista_servicos, name='lista_servicos'),
    path('editar_servicos/', admin_views.servicos_admin_list, name='servicos_admin_list'),
    path('editar_servicos/', admin_views.servico_admin_form, name='servico_admin_create'),
    path('editar_servicos/<str:pk>/editar/', admin_views.servico_admin_form, name='servico_admin_edit'),
    path('editar_servicos/<str:pk>/deletar/', admin_views.servico_admin_delete, name='servico_admin_delete'),

    # Gestão de Agendamentos
    path('agendamentos/fila/', admin_views.agendamentos_fila, name='agendamentos_fila'),
    path('agendamentos/historico/', admin_views.historico_agendamentos, name='historico_agendamentos'),
    path('agendamentos/<str:agendamento_id>/atualizar-status/', admin_views.atualizar_status_agendamento, name='atualizar_status_agendamento'),
    path('agendamentos/<str:agendamento_id>/cancelar/', admin_views.cancelar_agendamento, name='cancelar_agendamento'),
    path('agendamentos/<str:agendamento_id>/enviar-lembrete/', admin_views.enviar_lembrete, name='enviar_lembrete'),

    # Login / Logout
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Página de detalhes do serviço (usa ObjectId do MongoDB)
    path('servico/<str:servico_id>/', views.servico_detalhe, name='servico_detalhe'),
    
    # APIs AJAX
    path('api/agendar/', views.agendar_servico, name='agendar_servico'),
    path('api/buscar/', views.buscar_servicos_ajax, name='buscar_servicos'),
    path('api/horarios/', views.buscar_horarios_disponiveis, name='buscar_horarios'),
    
    # Dashboard administrativo
    path('dashboard/', admin_views.estatisticas_dashboard, name='dashboard'),
    path('dashboard/estatisticas-vendas/', admin_views.estatisticas_vendas_json, name='estatisticas_vendas_json'),
    
    # Gestão de Profissionais
    path('profissionais/', admin_views.profissionais_admin_list, name='profissionais_admin_list'),
    path('profissionais/novo/', admin_views.profissional_admin_form, name='profissional_admin_create'),
    path('profissionais/<str:pk>/editar/', admin_views.profissional_admin_form, name='profissional_admin_edit'),
    path('profissionais/<str:profissional_id>/horarios/', admin_views.horarios_profissional, name='horarios_profissional'),
    path('profissionais/<str:profissional_id>/criar-horarios/', admin_views.criar_horarios_diarios, name='criar_horarios_diarios'),
    path('horarios/<str:horario_id>/toggle/', admin_views.toggle_horario_disponivel, name='toggle_horario_disponivel'),
    path('horarios/<str:horario_id>/deletar/', admin_views.deletar_horario, name='deletar_horario'),
    
    # Controle de Barbearia (Abrir/Fechar)
    path('barbearia/toggle-status/', admin_views.toggle_status_barbearia, name='toggle_status_barbearia'),
    
    # APIs para Agent WhatsApp
    path('api/barbearia/status/', admin_views.api_status_barbearia, name='api_status_barbearia'),
    path('api/agendamento/cancelar/', admin_views.api_cancelar_agendamento_agent, name='api_cancelar_agendamento_agent'),
    path('api/servicos/disponiveis/', admin_views.api_servicos_disponiveis, name='api_servicos_disponiveis'),
    path('api/profissionais/disponiveis/', admin_views.api_profissionais_disponiveis, name='api_profissionais_disponiveis'),
    
    # Health check para monitoramento
    path('health/', admin_views.health_check, name='health_check'),
    
    # ============================================
    # ROTAS PARA VESTUÁRIO (Simplificado)
    # ============================================
    
    path('vestuario/', vestuario_views.vestuario_view, name='vestuario_view'),
    path('vestuario/produto/adicionar/', vestuario_views.produto_vestuario_adicionar, name='produto_vestuario_adicionar'),
    path('vestuario/venda/registrar/', vestuario_views.venda_vestuario, name='venda_vestuario'),
]