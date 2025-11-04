from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from servicos.models import Agendamento, Servico, Profissional
from datetime import datetime, timedelta

def lista_agendamentos(request):
    """Lista todos os agendamentos"""
    try:
        agendamentos = Agendamento.objects.all().order_by('-data_agendamento')
        context = {
            'agendamentos': agendamentos,
            'page_title': 'Agendamentos'
        }
        return render(request, 'agendamentos/lista_agendamentos.html', context)
    except Exception as e:
        print(f"❌ Erro ao listar agendamentos: {str(e)}")
        return render(request, 'agendamentos/lista_agendamentos.html', {
            'error': str(e),
            'page_title': 'Agendamentos'
        })

def criar_agendamento(request):
    """Cria um novo agendamento"""
    if request.method == 'POST':
        try:
            # Dados do formulário
            cliente_nome = request.POST.get('cliente_nome')
            cliente_telefone = request.POST.get('cliente_telefone')
            cliente_email = request.POST.get('cliente_email', '').strip() or None
            servico_id = request.POST.get('servico_id')
            profissional_id = request.POST.get('profissional_id')
            data_agendamento = request.POST.get('data_agendamento')
            hora_agendamento = request.POST.get('hora_agendamento')
            observacoes = request.POST.get('observacoes', '')
            
            # Buscar serviço e profissional
            servico = Servico.objects.get(id=servico_id)
            profissional = Profissional.objects.get(id=profissional_id)
            
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
                status='pendente'
            )
            
            agendamento.save()
            
            return redirect('detalhe_agendamento', agendamento_id=str(agendamento.id))
            
        except Exception as e:
            print(f"❌ Erro ao criar agendamento: {str(e)}")
            return render(request, 'agendamentos/criar_agendamento.html', {
                'error': str(e),
                'page_title': 'Criar Agendamento'
            })
    
    # GET - mostrar formulário
    try:
        servicos = Servico.objects(ativo=True).order_by('nome')
        profissionais = Profissional.objects(ativo=True).order_by('nome_completo')
        
        context = {
            'servicos': servicos,
            'profissionais': profissionais,
            'page_title': 'Criar Agendamento'
        }
        return render(request, 'agendamentos/criar_agendamento.html', context)
    except Exception as e:
        print(f"❌ Erro ao carregar formulário: {str(e)}")
        return render(request, 'agendamentos/criar_agendamento.html', {
            'error': str(e),
            'page_title': 'Criar Agendamento'
        })

def detalhe_agendamento(request, agendamento_id):
    """Detalhes de um agendamento"""
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        context = {
            'agendamento': agendamento,
            'page_title': f'Agendamento #{agendamento_id}'
        }
        return render(request, 'agendamentos/detalhe_agendamento.html', context)
    except Agendamento.DoesNotExist:
        return render(request, 'agendamentos/erro.html', {
            'mensagem': 'Agendamento não encontrado',
            'page_title': 'Erro'
        })
    except Exception as e:
        print(f"❌ Erro ao carregar agendamento: {str(e)}")
        return render(request, 'agendamentos/erro.html', {
            'mensagem': f'Erro ao carregar agendamento: {str(e)}',
            'page_title': 'Erro'
        })

def cancelar_agendamento(request, agendamento_id):
    """Cancela um agendamento"""
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        agendamento.status = 'cancelado'
        agendamento.save()
        
        return redirect('detalhe_agendamento', agendamento_id=agendamento_id)
    except Agendamento.DoesNotExist:
        return render(request, 'agendamentos/erro.html', {
            'mensagem': 'Agendamento não encontrado',
            'page_title': 'Erro'
        })
    except Exception as e:
        print(f"❌ Erro ao cancelar agendamento: {str(e)}")
        return render(request, 'agendamentos/erro.html', {
            'mensagem': f'Erro ao cancelar agendamento: {str(e)}',
            'page_title': 'Erro'
        })