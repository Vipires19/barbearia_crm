# servicos/vestuario_views.py

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required as staff_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
import json

from .models import ProdutoRoupa, VendaRoupa
from .models_mongo import ClienteMongo
from django.utils import timezone

@login_required
@staff_required
def vestuario_view(request):
    """View única para gerenciar vestuário - estoque + vendas"""
    try:
        # Buscar todos os produtos ativos
        produtos = ProdutoRoupa.objects(ativo=True).order_by('categoria', 'nome')
        
        # Preparar dados dos produtos para JavaScript de forma segura
        produtos_json = []
        for produto in produtos:
            produtos_json.append({
                'id': str(produto.id),
                'nome': produto.nome,
                'categoria': produto.categoria or '',
                'preco': float(produto.preco) if produto.preco else 0.0,
                'estoque_pp': int(produto.estoque_pp) if produto.estoque_pp else 0,
                'estoque_p': int(produto.estoque_p) if produto.estoque_p else 0,
                'estoque_m': int(produto.estoque_m) if produto.estoque_m else 0,
                'estoque_g': int(produto.estoque_g) if produto.estoque_g else 0,
                'estoque_gg': int(produto.estoque_gg) if produto.estoque_gg else 0,
            })
        
        import json
        context = {
            'produtos': produtos,
            'produtos_json': json.dumps(produtos_json),
            'page_title': 'Vestuário'
        }
        
        return render(request, 'servicos/roupas/vestuario.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao carregar vestuário: {str(e)}")
        import traceback
        import json
        traceback.print_exc()
        return render(request, 'servicos/roupas/vestuario.html', {
            'produtos': [],
            'produtos_json': json.dumps([]),
            'page_title': 'Vestuário'
        })

@login_required
@staff_required
def produto_vestuario_adicionar(request):
    """Adiciona um novo produto via modal"""
    if request.method == 'POST':
        try:
            # Função helper para converter valores seguramente
            def get_int(value, default=0):
                try:
                    return int(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            def get_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            # Criar produto
            produto = ProdutoRoupa(
                nome=request.POST.get('nome'),
                categoria=request.POST.get('categoria', ''),
                preco=get_float(request.POST.get('preco'), 0),
                preco_custo=get_float(request.POST.get('preco_custo'), 0),
                estoque_minimo=get_int(request.POST.get('estoque_minimo'), 5),
                estoque_pp=get_int(request.POST.get('estoque_pp')),
                estoque_p=get_int(request.POST.get('estoque_p')),
                estoque_m=get_int(request.POST.get('estoque_m')),
                estoque_g=get_int(request.POST.get('estoque_g')),
                estoque_gg=get_int(request.POST.get('estoque_gg')),
                marca=request.POST.get('marca', ''),
                cor=request.POST.get('cor', ''),
                material=request.POST.get('material', ''),
                ativo=True
            )
            produto.save()
            
            return JsonResponse({'success': True, 'message': 'Produto adicionado com sucesso!'})
            
        except Exception as e:
            print(f"❌ Erro ao adicionar produto: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
@staff_required
def venda_vestuario(request):
    """Registra uma nova venda de vestuário"""
    if request.method == 'POST':
        try:
            # Função helper para converter valores
            def get_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            # Dados do cliente
            cliente_nome = request.POST.get('cliente_nome')
            cliente_telefone = request.POST.get('cliente_telefone', '')
            forma_pagamento = request.POST.get('forma_pagamento')
            valor_desconto = get_float(request.POST.get('valor_desconto', 0))
            valor_total = get_float(request.POST.get('valor_total'))
            valor_pago = get_float(request.POST.get('valor_pago'))
            
            # Parse dos itens
            itens_json = request.POST.get('itens', '[]')
            itens = json.loads(itens_json)
            
            if not itens:
                return JsonResponse({'success': False, 'error': 'Nenhum item no pedido'})
            
            # Gerar número da venda
            numero_venda = VendaRoupa.gerar_numero_venda()
            
            # Calcular subtotal (sem desconto)
            subtotal = sum(item['preco'] * item['quantidade'] for item in itens)
            
            # Preparar itens para salvar e atualizar estoque
            itens_venda = []
            for item in itens:
                produto_id = item['produto_id']
                tamanho = item.get('tamanho', 'unico')
                quantidade = item['quantidade']
                
                try:
                    produto = ProdutoRoupa.objects.get(id=produto_id)
                except ProdutoRoupa.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Produto {produto_id} não encontrado'})
                
                itens_venda.append({
                    'produto_id': str(produto_id),
                    'produto_nome': item['produto_nome'],
                    'categoria': item.get('categoria', ''),
                    'tamanho': tamanho,
                    'quantidade': quantidade,
                    'preco_unitario': item['preco'],
                    'preco_total': item['preco'] * quantidade
                })
                
                # Atualizar estoque por tamanho
                if tamanho == 'pp':
                    produto.estoque_pp = max(0, (produto.estoque_pp or 0) - quantidade)
                elif tamanho == 'p':
                    produto.estoque_p = max(0, (produto.estoque_p or 0) - quantidade)
                elif tamanho == 'm':
                    produto.estoque_m = max(0, (produto.estoque_m or 0) - quantidade)
                elif tamanho == 'g':
                    produto.estoque_g = max(0, (produto.estoque_g or 0) - quantidade)
                elif tamanho == 'gg':
                    produto.estoque_gg = max(0, (produto.estoque_gg or 0) - quantidade)
                # Se for 'unico', não reduzimos estoque (produto sem tamanho específico)
                
                # Salvar produto com estoque atualizado
                produto.save()
            
            # Criar venda
            venda = VendaRoupa(
                numero_venda=numero_venda,
                cliente_nome=cliente_nome,
                cliente_telefone=cliente_telefone,
                itens=itens_venda,
                subtotal=subtotal,
                desconto=valor_desconto,
                valor_total=valor_total,
                forma_pagamento=forma_pagamento,
                vendedor=request.user.username if request.user else ''
            )
            venda.save()
            
            # Criar ou atualizar cliente (só se tiver telefone)
            if cliente_telefone:
                try:
                    # No MongoEngine, get_or_create funciona diretamente no manager
                    cliente_existente = ClienteMongo.objects(telefone=cliente_telefone).first()
                    
                    if cliente_existente:
                        # Atualizar cliente existente
                        cliente_existente.nome = cliente_nome
                        cliente_existente.ultima_compra = timezone.now()
                        cliente_existente.save()
                        try:
                            cliente_existente.atualizar_estatisticas()
                        except:
                            pass  # Se der erro, continua mesmo assim
                    else:
                        # Criar novo cliente
                        novo_cliente = ClienteMongo(
                            nome=cliente_nome,
                            telefone=cliente_telefone,
                            ultima_compra=timezone.now()
                        )
                        novo_cliente.save()
                        
                except Exception as e:
                    print(f"⚠️ Erro ao criar/atualizar cliente: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Não bloqueia a venda se der erro no cliente
            
            # Redirecionar para a mesma página
            return JsonResponse({
                'success': True, 
                'message': f'Venda #{numero_venda} registrada com sucesso!'
            })
            
        except Exception as e:
            print(f"❌ Erro ao registrar venda: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

