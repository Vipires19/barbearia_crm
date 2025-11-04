# servicos/admin_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required as staff_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import (
    Servico, Profissional, Agendamento, ConfiguracaoBarbearia, HorarioDisponivel,
    ProdutoRoupa, CategoriaRoupa, VendaRoupa
)
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

@login_required
@staff_required
def estatisticas_dashboard(request):
    """Dashboard com estatísticas gerais"""
    try:
        # Estatísticas básicas
        total_servicos = Servico.objects.count()
        total_profissionais = Profissional.objects.count()
        total_agendamentos = Agendamento.objects.count()
        
        # Agendamentos recentes
        agendamentos_recentes = Agendamento.objects.order_by('-data_criacao')[:10]
        
        # Agendamentos por status
        agendamentos_pendentes = Agendamento.objects(status='pendente').count()
        agendamentos_confirmados = Agendamento.objects(status='confirmado').count()
        agendamentos_concluidos = Agendamento.objects(status='concluido').count()
        
        # Estatísticas de Roupas
        total_produtos_roupa = ProdutoRoupa.objects.count()
        produtos_estoque_baixo = ProdutoRoupa.produtos_estoque_baixo()
        total_vendas_roupa = VendaRoupa.objects.count()
        
        # Vendas de hoje (roupas)
        vendas_hoje_roupa = VendaRoupa.vendas_hoje()
        total_hoje_roupa = sum(float(v.valor_total) for v in vendas_hoje_roupa)
        
        # Configuração da barbearia
        config = ConfiguracaoBarbearia.get_configuracao()
        
        context = {
            'total_servicos': total_servicos,
            'total_profissionais': total_profissionais,
            'total_agendamentos': total_agendamentos,
            'agendamentos_recentes': agendamentos_recentes,
            'agendamentos_pendentes': agendamentos_pendentes,
            'agendamentos_confirmados': agendamentos_confirmados,
            'agendamentos_concluidos': agendamentos_concluidos,
            'config': config,
            # Estatísticas de roupas
            'total_produtos_roupa': total_produtos_roupa,
            'produtos_estoque_baixo': produtos_estoque_baixo,
            'total_vendas_roupa': total_vendas_roupa,
            'total_hoje_roupa': total_hoje_roupa,
            'page_title': 'Dashboard - Barbearia'
        }
        
        return render(request, 'servicos/admin/dashboard.html', context)
        
    except Exception as e:
        print(f"Erro no dashboard: {str(e)}")
        return render(request, 'servicos/admin/dashboard.html', {
            'error': str(e),
            'page_title': 'Dashboard - Barbearia'
        })

@login_required
@staff_required
def servicos_admin_list(request):
    """Lista todos os serviços"""
    try:
        servicos = Servico.objects.all().order_by('categoria', 'nome')
        context = {
            'servicos': servicos,
            'page_title': 'Gerenciar Serviços'
        }
        return render(request, 'servicos/admin/lista_servicos.html', context)
    except Exception as e:
        print(f"Erro ao listar serviços: {str(e)}")
        return render(request, 'servicos/admin/lista_servicos.html', {
            'error': str(e),
            'page_title': 'Gerenciar Serviços'
        })

@login_required
@staff_required
def servico_admin_form(request, pk=None):
    """Formulário para criar/editar serviço"""
    try:
        if pk:
            servico = Servico.objects.get(id=pk)
            is_edit = True
        else:
            servico = None
            is_edit = False
        
        if request.method == 'POST':
            # Processar formulário
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao')
            preco = float(request.POST.get('preco', 0))
            categoria = request.POST.get('categoria')
            duracao_minutos = int(request.POST.get('duracao_minutos', 30))
            
            if is_edit:
                servico.nome = nome
                servico.descricao = descricao
                servico.preco = preco
                servico.categoria = categoria
                servico.duracao_minutos = duracao_minutos
            else:
                servico = Servico(
                    nome=nome,
                    descricao=descricao,
                    preco=preco,
                    categoria=categoria,
                    duracao_minutos=duracao_minutos,
                    disponivel=True
                )
            
            # Salvar imagem se fornecida
            if 'imagem' in request.FILES:
                imagem = request.FILES['imagem']
                nome_arquivo = f"servicos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{imagem.name}"
                caminho_imagem = default_storage.save(nome_arquivo, ContentFile(imagem.read()))
                servico.imagem = caminho_imagem
            
            servico.save()
            return redirect('servicos_admin_list')
        
        # GET - mostrar formulário
        context = {
            'servico': servico,
            'is_edit': is_edit,
            'page_title': 'Editar Serviço' if is_edit else 'Criar Serviço'
        }
        return render(request, 'servicos/admin/servico_form.html', context)
        
    except Exception as e:
        print(f"Erro no formulário: {str(e)}")
        return render(request, 'servicos/admin/servico_form.html', {
            'error': str(e),
            'page_title': 'Erro no Formulário'
        })

@login_required
@staff_required
def servico_admin_delete(request, pk):
    """Deletar serviço"""
    try:
        servico = Servico.objects.get(id=pk)
        servico.delete()
        return redirect('servicos_admin_list')
    except Exception as e:
        print(f"Erro ao deletar serviço: {str(e)}")
        return redirect('servicos_admin_list')

@login_required
@staff_required
def agendamentos_fila(request):
    """Lista agendamentos em fila"""
    try:
        agendamentos = Agendamento.objects.all().order_by('-data_agendamento')
        context = {
            'agendamentos': agendamentos,
            'page_title': 'Agendamentos'
        }
        return render(request, 'servicos/admin/agendamentos_fila.html', context)
    except Exception as e:
        print(f"Erro ao listar agendamentos: {str(e)}")
        return render(request, 'servicos/admin/agendamentos_fila.html', {
            'error': str(e),
            'page_title': 'Agendamentos'
        })

@login_required
@staff_required
def atualizar_status_agendamento(request, agendamento_id):
    """Atualiza status de um agendamento"""
    if request.method == 'POST':
        try:
            agendamento = Agendamento.objects.get(id=agendamento_id)
            novo_status = request.POST.get('status')
            
            if novo_status in ['pendente', 'confirmado', 'cancelado', 'concluido']:
                agendamento.status = novo_status
                agendamento.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status atualizado para {novo_status}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Status inválido'
                })
                
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Agendamento não encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })

@login_required
@staff_required
def cancelar_agendamento(request, agendamento_id):
    """Cancela um agendamento"""
    if request.method == 'POST':
        try:
            agendamento = Agendamento.objects.get(id=agendamento_id)
            agendamento.status = 'cancelado'
            agendamento.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Agendamento cancelado com sucesso!'
            })
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Agendamento não encontrado'
            })
        except Exception as e:
            print(f"Erro ao cancelar agendamento: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })

@login_required
@staff_required
def enviar_lembrete(request, agendamento_id):
    """Envia lembrete de agendamento via WhatsApp"""
    if request.method == 'POST':
        try:
            agendamento = Agendamento.objects.get(id=agendamento_id)
            
            # Tentar importar e usar a integração WhatsApp
            try:
                from barbearia.whatsapp_integration import whatsapp_api
                
                if whatsapp_api.send_reminder(agendamento):
                    return JsonResponse({
                        'success': True,
                        'message': 'Lembrete enviado com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Erro ao enviar lembrete via WhatsApp'
                    })
            except ImportError:
                # Se WhatsApp não estiver configurado, retornar mensagem informativa
                return JsonResponse({
                    'success': False,
                    'message': 'WhatsApp não está configurado. Configure o WAHA para enviar lembretes.'
                })
            except Exception as e:
                print(f"Erro ao enviar lembrete: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao enviar lembrete: {str(e)}'
                })
                
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Agendamento não encontrado'
            })
        except Exception as e:
            print(f"Erro ao buscar agendamento: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })

@login_required
@staff_required
def historico_agendamentos(request):
    """Histórico de agendamentos com filtros por data e serviço"""
    try:
        # Obter filtros
        data_filtro = request.GET.get('data', datetime.now().strftime('%Y-%m-%d'))
        servico_id = request.GET.get('servico', '')
        
        # Converter string para date
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
        except:
            data_obj = datetime.now().date()
        
        # Buscar agendamentos do dia
        # Converter data para datetime para comparação
        from datetime import time as dt_time
        data_inicio = datetime.combine(data_obj, dt_time.min)
        data_fim = datetime.combine(data_obj + timedelta(days=1), dt_time.min)
        
        agendamentos = Agendamento.objects(
            data_agendamento__gte=data_inicio,
            data_agendamento__lt=data_fim
        ).order_by('hora_agendamento')
        
        # Filtrar por serviço se selecionado
        if servico_id:
            try:
                servico_filtro = Servico.objects.get(id=servico_id)
                agendamentos = agendamentos.filter(servico=servico_filtro)
            except:
                pass
        
        # Buscar todos os serviços para o filtro
        servicos = Servico.objects.all().order_by('nome')
        
        context = {
            'agendamentos': agendamentos,
            'servicos': servicos,
            'data_filtro': data_filtro,
            'servico_filtro': servico_id,
            'page_title': 'Histórico de Agendamentos'
        }
        return render(request, 'servicos/admin/historico_agendamentos.html', context)
        
    except Exception as e:
        print(f"Erro ao buscar histórico: {str(e)}")
        return render(request, 'servicos/admin/historico_agendamentos.html', {
            'error': str(e),
            'agendamentos': [],
            'servicos': Servico.objects.all().order_by('nome'),
            'data_filtro': datetime.now().strftime('%Y-%m-%d'),
            'servico_filtro': '',
            'page_title': 'Histórico de Agendamentos'
        })

@login_required
@staff_required
def profissionais_admin_list(request):
    """Lista todos os profissionais"""
    try:
        profissionais = Profissional.objects.all().order_by('nome_completo')
        context = {
            'profissionais': profissionais,
            'page_title': 'Gerenciar Profissionais'
        }
        return render(request, 'servicos/admin/lista_profissionais.html', context)
    except Exception as e:
        print(f"Erro ao listar profissionais: {str(e)}")
        return render(request, 'servicos/admin/lista_profissionais.html', {
            'error': str(e),
            'page_title': 'Gerenciar Profissionais'
        })

@login_required
@staff_required
def profissional_admin_form(request, pk=None):
    """Formulário para criar/editar profissional"""
    try:
        if pk:
            profissional = Profissional.objects.get(id=pk)
            is_edit = True
        else:
            profissional = None
            is_edit = False
        
        if request.method == 'POST':
            # Processar formulário
            nome_completo = request.POST.get('nome_completo')
            especialidades_text = request.POST.get('especialidades', '')
            telefone = request.POST.get('telefone')
            email = request.POST.get('email')
            
            # Converter especialidades de string para lista
            especialidades = [esp.strip() for esp in especialidades_text.split(',') if esp.strip()]
            
            # Validar email - se estiver vazio, usar None
            if not email or email.strip() == '':
                email = None
            
            if is_edit:
                profissional.nome_completo = nome_completo
                profissional.especialidades = especialidades
                profissional.telefone = telefone
                profissional.email = email
            else:
                profissional = Profissional(
                    nome_completo=nome_completo,
                    especialidades=especialidades,
                    telefone=telefone,
                    email=email,
                    ativo=True
                )
            
            # Salvar foto se fornecida
            if 'foto' in request.FILES:
                foto = request.FILES['foto']
                nome_arquivo = f"profissionais/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{foto.name}"
                caminho_foto = default_storage.save(nome_arquivo, ContentFile(foto.read()))
                profissional.foto = caminho_foto
            
            profissional.save()
            return redirect('profissionais_admin_list')
        
        # GET - mostrar formulário
        context = {
            'profissional': profissional,
            'is_edit': is_edit,
            'page_title': 'Editar Profissional' if is_edit else 'Criar Profissional'
        }
        return render(request, 'servicos/admin/profissional_form.html', context)
        
    except Exception as e:
        print(f"Erro no formulário: {str(e)}")
        return render(request, 'servicos/admin/profissional_form.html', {
            'error': str(e),
            'page_title': 'Erro no Formulário'
        })

@login_required
@staff_required
def toggle_status_barbearia(request):
    """Alterna status da barbearia (aberta/fechada)"""
    try:
        config = ConfiguracaoBarbearia.get_configuracao()
        config.aberta = not config.aberta
        config.save()
        
        status = "aberta" if config.aberta else "fechada"
        return JsonResponse({
            'success': True,
            'message': f'Barbearia {status}',
            'status': config.aberta
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        })

def api_status_barbearia(request):
    """API para verificar status da barbearia"""
    try:
        config = ConfiguracaoBarbearia.get_configuracao()
        return JsonResponse({
            'aberta': config.aberta,
            'funcionando': config.esta_funcionando
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def api_servicos_disponiveis(request):
    """API para listar serviços disponíveis"""
    try:
        servicos = Servico.objects(disponivel=True).order_by('nome')
        servicos_data = []
        for servico in servicos:
            servicos_data.append({
                'id': str(servico.id),
                'nome': servico.nome,
                'descricao': servico.descricao,
                'preco': float(servico.preco),
                'duracao_minutos': servico.duracao_minutos
            })
        return JsonResponse({
            'servicos': servicos_data
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def api_profissionais_disponiveis(request):
    """API para listar profissionais disponíveis"""
    try:
        profissionais = Profissional.objects(ativo=True).order_by('nome_completo')
        profissionais_data = []
        for profissional in profissionais:
            profissionais_data.append({
                'id': str(profissional.id),
                'nome': profissional.nome_completo,
                'especialidades': profissional.especialidades
            })
        return JsonResponse({
            'profissionais': profissionais_data
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def api_cancelar_agendamento_agent(request):
    """API para cancelar agendamento via agent"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            agendamento_id = data.get('agendamento_id')
            
            agendamento = Agendamento.objects.get(id=agendamento_id)
            agendamento.status = 'cancelado'
            agendamento.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Agendamento cancelado com sucesso'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    })

def health_check(request):
    """Health check para monitoramento"""
    return JsonResponse({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@login_required
@staff_required
def horarios_profissional(request, profissional_id):
    """Lista horários disponíveis de um profissional"""
    try:
        profissional = Profissional.objects.get(id=profissional_id)
        data_filtro = request.GET.get('data', datetime.now().strftime('%Y-%m-%d'))
        
        # Converter string para date
        data = datetime.strptime(data_filtro, '%Y-%m-%d').date()
        
        horarios = HorarioDisponivel.get_horarios_disponiveis(profissional, data)
        
        context = {
            'profissional': profissional,
            'horarios': horarios,
            'data_filtro': data_filtro,
            'page_title': f'Horários - {profissional.nome_completo}'
        }
        return render(request, 'servicos/admin/horarios_profissional.html', context)
        
    except Exception as e:
        print(f"Erro ao listar horários: {str(e)}")
        return render(request, 'servicos/admin/horarios_profissional.html', {
            'error': str(e),
            'page_title': 'Erro ao Listar Horários'
        })

@login_required
@staff_required
def criar_horarios_diarios(request, profissional_id):
    """Cria horários disponíveis para um dia"""
    try:
        profissional = Profissional.objects.get(id=profissional_id)
        
        if request.method == 'POST':
            data = request.POST.get('data')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fim = request.POST.get('hora_fim')
            intervalo = int(request.POST.get('intervalo', 30))
            observacoes = request.POST.get('observacoes', '')
            
            # Converter string para date
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            
            # Criar horários
            horarios_criados = HorarioDisponivel.criar_horarios_diarios(
                profissional, data_obj, hora_inicio, hora_fim, intervalo
            )
            
            # Adicionar observações aos horários criados
            for horario in horarios_criados:
                if observacoes:
                    horario.observacoes = observacoes
                    horario.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{len(horarios_criados)} horários criados com sucesso!'
            })
        
        # GET - mostrar formulário
        context = {
            'profissional': profissional,
            'page_title': f'Criar Horários - {profissional.nome_completo}'
        }
        return render(request, 'servicos/admin/criar_horarios.html', context)
        
    except Exception as e:
        print(f"Erro ao criar horários: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        })

@login_required
@staff_required
def toggle_horario_disponivel(request, horario_id):
    """Alterna disponibilidade de um horário"""
    try:
        horario = HorarioDisponivel.objects.get(id=horario_id)
        horario.disponivel = not horario.disponivel
        horario.save()
        
        status = "disponível" if horario.disponivel else "indisponível"
        return JsonResponse({
            'success': True,
            'message': f'Horário marcado como {status}',
            'disponivel': horario.disponivel
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        })

@login_required
@staff_required
def deletar_horario(request, horario_id):
    """Deleta um horário"""
    try:
        horario = HorarioDisponivel.objects.get(id=horario_id)
        profissional_id = str(horario.profissional.id)
        horario.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Horário deletado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        })


@login_required
@staff_required
def estatisticas_vendas_json(request):
    """Retorna estatísticas de vendas em JSON para o dashboard"""
    try:
        # Parâmetros de período (padrão: últimos 30 dias)
        periodo = request.GET.get('periodo', '30')  # dias
        try:
            dias = int(periodo)
        except:
            dias = 30
        
        data_fim = timezone.now()
        data_inicio = data_fim - timedelta(days=dias)
        
        # Filtrar vendas no período (apenas concluídas)
        vendas = VendaRoupa.objects(
            data_venda__gte=data_inicio,
            data_venda__lte=data_fim,
            status='concluida'
        )
        
        total_vendas = vendas.count()
        
        # 1. Total de vendas no período
        total_vendas_periodo = total_vendas
        
        # 2. Faturamento bruto e líquido
        faturamento_bruto = sum(float(v.subtotal) for v in vendas)
        total_descontos = sum(float(v.desconto) for v in vendas)
        faturamento_liquido = faturamento_bruto - total_descontos
        
        # 3. Ticket médio
        ticket_medio = faturamento_liquido / total_vendas if total_vendas > 0 else 0
        
        # 4. Desconto médio
        desconto_medio = total_descontos / total_vendas if total_vendas > 0 else 0
        
        # 5. Vendas por forma de pagamento
        vendas_por_pagamento = defaultdict(float)
        vendas_count_por_pagamento = defaultdict(int)
        
        for venda in vendas:
            forma_pag = venda.forma_pagamento or 'outro'
            vendas_por_pagamento[forma_pag] += float(venda.valor_total)
            vendas_count_por_pagamento[forma_pag] += 1
        
        vendas_por_pagamento_dict = {
            'dinheiro': {
                'valor': vendas_por_pagamento.get('dinheiro', 0),
                'quantidade': vendas_count_por_pagamento.get('dinheiro', 0)
            },
            'debito': {
                'valor': vendas_por_pagamento.get('debito', 0),
                'quantidade': vendas_count_por_pagamento.get('debito', 0)
            },
            'credito': {
                'valor': vendas_por_pagamento.get('credito', 0),
                'quantidade': vendas_count_por_pagamento.get('credito', 0)
            },
            'pix': {
                'valor': vendas_por_pagamento.get('pix', 0),
                'quantidade': vendas_count_por_pagamento.get('pix', 0)
            },
            'outro': {
                'valor': vendas_por_pagamento.get('outro', 0),
                'quantidade': vendas_count_por_pagamento.get('outro', 0)
            }
        }
        
        # 6. Vendas por vendedor
        vendas_por_vendedor = defaultdict(float)
        vendas_count_por_vendedor = defaultdict(int)
        
        for venda in vendas:
            vendedor = venda.vendedor or 'Não informado'
            vendas_por_vendedor[vendedor] += float(venda.valor_total)
            vendas_count_por_vendedor[vendedor] += 1
        
        vendas_por_vendedor_list = [
            {
                'vendedor': vendedor,
                'valor_total': float(vendas_por_vendedor[vendedor]),
                'quantidade': vendas_count_por_vendedor[vendedor]
            }
            for vendedor in sorted(vendas_por_vendedor.keys(), key=lambda x: vendas_por_vendedor[x], reverse=True)
        ]
        
        # 7. Quantidade de clientes únicos
        clientes_unicos = set()
        for venda in vendas:
            if venda.cliente_telefone:
                clientes_unicos.add(venda.cliente_telefone)
            elif venda.cliente_nome:
                # Se não tiver telefone, usa nome como identificador
                clientes_unicos.add(venda.cliente_nome.lower().strip())
        
        quantidade_clientes_unicos = len(clientes_unicos)
        
        # 8. Serviços/Produtos mais vendidos (a partir de itens)
        produtos_vendidos = Counter()
        produtos_quantidade = Counter()
        
        for venda in vendas:
            for item in venda.itens:
                produto_nome = item.get('produto_nome', 'Produto Desconhecido')
                quantidade = item.get('quantidade', 0)
                # O campo no item pode ser 'preco' ou 'preco_unitario'
                preco_unit = float(item.get('preco', 0) or item.get('preco_unitario', 0))
                produtos_vendidos[produto_nome] += preco_unit * quantidade
                produtos_quantidade[produto_nome] += quantidade
        
        produtos_mais_vendidos = [
            {
                'produto': produto,
                'valor_total': float(produtos_vendidos[produto]),
                'quantidade': int(produtos_quantidade[produto])
            }
            for produto, _ in produtos_vendidos.most_common(10)
        ]
        
        # 9. Comparativo de vendas por dia da semana
        vendas_por_dia_semana = defaultdict(float)
        vendas_count_por_dia = defaultdict(int)
        
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for venda in vendas:
            # MongoEngine retorna datetime, garantindo que seja datetime
            data_venda = venda.data_venda
            if isinstance(data_venda, datetime):
                dia_semana_num = data_venda.weekday()  # 0 = Segunda, 6 = Domingo
            elif hasattr(data_venda, 'weekday'):
                dia_semana_num = data_venda.weekday()
            else:
                continue
            
            dia_semana_nome = dias_semana[dia_semana_num]
            vendas_por_dia_semana[dia_semana_nome] += float(venda.valor_total)
            vendas_count_por_dia[dia_semana_nome] += 1
        
        comparativo_dia_semana = [
            {
                'dia': dia,
                'valor_total': float(vendas_por_dia_semana.get(dia, 0)),
                'quantidade': vendas_count_por_dia.get(dia, 0)
            }
            for dia in dias_semana
        ]
        
        # Preparar resposta JSON
        resultado = {
            'success': True,
            'periodo': {
                'dias': dias,
                'data_inicio': data_inicio.isoformat(),
                'data_fim': data_fim.isoformat()
            },
            'kpis': {
                'total_vendas': total_vendas_periodo,
                'faturamento_bruto': round(float(faturamento_bruto), 2),
                'faturamento_liquido': round(float(faturamento_liquido), 2),
                'total_descontos': round(float(total_descontos), 2),
                'ticket_medio': round(float(ticket_medio), 2),
                'desconto_medio': round(float(desconto_medio), 2),
                'quantidade_clientes_unicos': quantidade_clientes_unicos
            },
            'vendas_por_pagamento': vendas_por_pagamento_dict,
            'vendas_por_vendedor': vendas_por_vendedor_list,
            'produtos_mais_vendidos': produtos_mais_vendidos,
            'comparativo_dia_semana': comparativo_dia_semana
        }
        
        return JsonResponse(resultado, safe=False)
        
    except Exception as e:
        print(f"❌ Erro ao calcular estatísticas de vendas: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)