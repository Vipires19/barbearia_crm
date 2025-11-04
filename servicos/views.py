from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from mongoengine import DoesNotExist
from .models import Servico, Agendamento, Profissional, ConfiguracaoBarbearia, HorarioDisponivel
import json
from datetime import datetime, timedelta

# Create your views here.

def lista_servicos(request):
    """
    View que exibe a lista de serviços da barbearia
    """
    # Verificar se a barbearia está funcionando
    try:
        config = ConfiguracaoBarbearia.get_configuracao()
        
        if not config.esta_funcionando:
            return render(request, 'servicos/barbearia_fechada.html', {
                'config': config,
                'page_title': 'Barbearia Fechada'
            })
    except:
        pass
    
    # Parâmetros de filtro
    categoria = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()
    
    # Busca serviços
    servicos = Servico.buscar_servicos(
        termo_busca=busca if busca else None,
        categoria=categoria,
        apenas_disponiveis=True
    )
    
    # Converte QuerySet do MongoEngine para lista para paginação
    servicos_list = list(servicos)
    
    # Paginação - 12 serviços por página
    paginator = Paginator(servicos_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Busca categorias disponíveis
    categorias = Servico.get_categorias()
    
    context = {
        'servicos': page_obj,
        'categorias': categorias,
        'categoria_atual': categoria,
        'busca_atual': busca,
        'total_servicos': len(servicos_list),
        'page_title': 'Serviços Disponíveis'
    }
    
    return render(request, 'servicos/lista_servicos.html', context)

def servico_detalhe(request, servico_id):
    """
    View que exibe os detalhes de um serviço específico
    """
    try:
        # Buscar serviço
        servico = Servico.objects.get(id=servico_id)
        
        # Preparar contexto com tratamento de tipos
        context = {
            'servico': servico,
            'page_title': f'{servico.nome} - Detalhes'
        }
        
        # Debug: verificar tipos
        print(f"📊 Serviço: {servico.nome}")
        print(f"📊 Tipo de categoria: {type(servico.categoria)}")
        print(f"📊 Profissionais habilitados: {servico.profissionais_habilitados}")
        
        return render(request, 'servicos/servico_detalhe.html', context)
        
    except Servico.DoesNotExist:
        return render(request, 'servicos/erro.html', {
            'mensagem': 'Serviço não encontrado',
            'page_title': 'Erro'
        })
    except Exception as e:
        import traceback
        print(f"❌ Erro ao carregar serviço: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return render(request, 'servicos/erro.html', {
            'mensagem': f'Erro ao carregar serviço: {str(e)}',
            'page_title': 'Erro'
        })

@require_http_methods(["GET", "POST"])
def agendar_servico(request):
    """
    View para agendar um serviço
    """
    if request.method == 'POST':
        try:
            # Processar agendamento
            data = json.loads(request.body)
            
            cliente_nome = data.get('cliente_nome')
            cliente_telefone = data.get('cliente_telefone')
            cliente_email = data.get('cliente_email', '').strip() or None
            servico_id = data.get('servico_id')
            profissional_id = data.get('profissional_id')
            data_agendamento = data.get('data_agendamento')
            hora_agendamento = data.get('hora_agendamento')
            observacoes = data.get('observacoes', '')
            
            # Buscar serviço e profissional
            servico = Servico.objects.get(id=servico_id)
            profissional = Profissional.objects.get(id=profissional_id)
            
            # Calcular valor total
            valor_total = float(servico.preco)
            
            # Criar agendamento
            agendamento = Agendamento(
                cliente_nome=cliente_nome,
                cliente_telefone=cliente_telefone,
                cliente_email=cliente_email,
                servico=servico,
                profissional=profissional,
                data_agendamento=datetime.strptime(data_agendamento, '%Y-%m-%d'),
                hora_agendamento=hora_agendamento,
                observacoes=observacoes,
                valor_total=valor_total,
                status='pendente'
            )
            
            agendamento.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Agendamento realizado com sucesso!',
                'agendamento_id': str(agendamento.id)
            })
            
        except Exception as e:
            print(f"❌ Erro ao criar agendamento: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar agendamento: {str(e)}'
            })
    
    # GET - mostrar formulário de agendamento
    try:
        servico_id = request.GET.get('servico_id')
        servico = None
        
        if servico_id:
            servico = Servico.objects.get(id=servico_id)
            profissionais = servico.profissionais_habilitados if servico.profissionais_habilitados else Profissional.objects(ativo=True)
        else:
            # Se não especificou serviço, mostrar todos os profissionais
            profissionais = Profissional.objects(ativo=True)
        
        # Buscar todos os serviços para seleção
        servicos = Servico.objects.filter(ativo=True).order_by('nome')
        
        context = {
            'servico': servico,
            'servicos': servicos,
            'profissionais': profissionais,
            'page_title': f'Agendar {servico.nome}' if servico else 'Agendar Serviço'
        }
        
        return render(request, 'servicos/agendar_servico.html', context)
        
    except Servico.DoesNotExist:
        return render(request, 'servicos/erro.html', {
            'mensagem': 'Serviço não encontrado',
            'page_title': 'Erro'
        })
    except Exception as e:
        print(f"❌ Erro ao agendar serviço: {str(e)}")
        return render(request, 'servicos/erro.html', {
            'mensagem': f'Erro ao agendar serviço: {str(e)}',
            'page_title': 'Erro'
        })

@require_http_methods(["GET"])
def buscar_servicos_ajax(request):
    """
    API AJAX para buscar serviços
    """
    try:
        termo = request.GET.get('q', '').strip()
        
        if len(termo) < 2:
            return JsonResponse({
                'servicos': []
            })
        
        # Buscar serviços
        servicos = Servico.buscar_servicos(
            termo_busca=termo,
            apenas_disponiveis=True
        )
        
        # Converter para JSON
        servicos_data = []
        for servico in servicos[:10]:  # Limitar a 10 resultados
            servicos_data.append({
                'id': str(servico.id),
                'nome': servico.nome,
                'descricao': servico.descricao,
                'preco': float(servico.preco),
                'categoria': servico.categoria.nome if servico.categoria else 'Outros'
            })
        
        return JsonResponse({
            'servicos': servicos_data
        })
        
    except Exception as e:
        print(f"❌ Erro na busca: {str(e)}")
        return JsonResponse({
            'servicos': []
        })

@require_http_methods(["GET"])
def buscar_horarios_disponiveis(request):
    """
    API AJAX para buscar horários disponíveis de um profissional em uma data
    """
    try:
        profissional_id = request.GET.get('profissional_id')
        data_agendamento = request.GET.get('data')
        
        if not profissional_id or not data_agendamento:
            return JsonResponse({
                'horarios': [],
                'message': 'Profissional e data são obrigatórios'
            })
        
        # Converter string para date
        data_obj = datetime.strptime(data_agendamento, '%Y-%m-%d').date()
        
        # Buscar profissional
        profissional = Profissional.objects.get(id=profissional_id)
        
        # Buscar horários disponíveis
        horarios = HorarioDisponivel.get_horarios_disponiveis(profissional, data_obj)
        
        # Converter para JSON
        horarios_data = []
        for horario in horarios:
            horarios_data.append({
                'id': str(horario.id),
                'hora_inicio': horario.hora_inicio,
                'hora_fim': horario.hora_fim,
                'disponivel': horario.disponivel,
                'observacoes': horario.observacoes or ''
            })
        
        return JsonResponse({
            'horarios': horarios_data,
            'profissional': {
                'id': str(profissional.id),
                'nome': profissional.nome_completo,
                'especialidades': profissional.especialidades
            }
        })
        
    except Profissional.DoesNotExist:
        return JsonResponse({
            'horarios': [],
            'message': 'Profissional não encontrado'
        })
    except Exception as e:
        print(f"❌ Erro ao buscar horários: {str(e)}")
        return JsonResponse({
            'horarios': [],
            'message': f'Erro ao buscar horários: {str(e)}'
        })