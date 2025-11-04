# servicos/roupas_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required as staff_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import ProdutoRoupa, VendaRoupa

# ============================================
# VIEWS PARA PRODUTOS DE ROUPA
# ============================================

@login_required
@staff_required
def produtos_lista(request):
    """Lista todos os produtos de roupa"""
    try:
        # Parâmetros de filtro
        categoria_id = request.GET.get('categoria')
        busca = request.GET.get('busca', '').strip()
        estoque_baixo = request.GET.get('estoque_baixo', False)
        
        # Buscar produtos
        if categoria_id:
            produtos = ProdutoRoupa.objects(categoria=categoria_id)
        else:
            produtos = ProdutoRoupa.objects.all()
        
        # Filtro de busca
        if busca:
            produtos = produtos.filter(nome__icontains=busca)
        
        # Filtro de estoque baixo
        if estoque_baixo:
            produtos = [p for p in produtos if p.estoque_baixo]
        
        # Ordenar
        produtos = sorted(produtos, key=lambda x: (x.categoria.nome if x.categoria else '', x.nome))
        
        # Paginação
        paginator = Paginator(produtos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Buscar categorias
        categorias = CategoriaRoupa.objects(ativo=True).order_by('nome')
        
        context = {
            'produtos': page_obj,
            'categorias': categorias,
            'categoria_selecionada': categoria_id,
            'busca': busca,
            'estoque_baixo': estoque_baixo,
            'page_title': 'Produtos de Roupa'
        }
        
        return render(request, 'servicos/roupas/produtos_lista.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao listar produtos: {str(e)}")
        return render(request, 'servicos/roupas/produtos_lista.html', {
            'produtos': [],
            'categorias': [],
            'page_title': 'Produtos de Roupa'
        })

@login_required
@staff_required
def produto_form(request, pk=None):
    """Cria ou edita um produto de roupa"""
    try:
        produto = None
        if pk:
            produto = ProdutoRoupa.objects.get(id=pk)
        
        if request.method == 'POST':
            # Processar formulário
            nome = request.POST.get('nome')
            categoria_id = request.POST.get('categoria')
            preco = float(request.POST.get('preco', 0))
            preco_custo = float(request.POST.get('preco_custo', 0))
            estoque_minimo = int(request.POST.get('estoque_minimo', 5))
            
            # Tamanhos
            estoque_pp = int(request.POST.get('estoque_pp', 0))
            estoque_p = int(request.POST.get('estoque_p', 0))
            estoque_m = int(request.POST.get('estoque_m', 0))
            estoque_g = int(request.POST.get('estoque_g', 0))
            estoque_gg = int(request.POST.get('estoque_gg', 0))
            
            marca = request.POST.get('marca', '')
            cor = request.POST.get('cor', '')
            material = request.POST.get('material', '')
            ativo = request.POST.get('ativo') == 'on'
            em_destaque = request.POST.get('em_destaque') == 'on'
            
            # Criar ou atualizar produto
            if not produto:
                categoria = CategoriaRoupa.objects.get(id=categoria_id)
                produto = ProdutoRoupa(
                    nome=nome,
                    categoria=categoria,
                    preco=preco,
                    preco_custo=preco_custo,
                    estoque_minimo=estoque_minimo,
                    estoque_pp=estoque_pp,
                    estoque_p=estoque_p,
                    estoque_m=estoque_m,
                    estoque_g=estoque_g,
                    estoque_gg=estoque_gg,
                    marca=marca,
                    cor=cor,
                    material=material,
                    ativo=ativo,
                    em_destaque=em_destaque
                )
            else:
                produto.nome = nome
                produto.categoria = CategoriaRoupa.objects.get(id=categoria_id)
                produto.preco = preco
                produto.preco_custo = preco_custo
                produto.estoque_minimo = estoque_minimo
                produto.estoque_pp = estoque_pp
                produto.estoque_p = estoque_p
                produto.estoque_m = estoque_m
                produto.estoque_g = estoque_g
                produto.estoque_gg = estoque_gg
                produto.marca = marca
                produto.cor = cor
                produto.material = material
                produto.ativo = ativo
                produto.em_destaque = em_destaque
            
            # Processar imagem se houver
            if 'imagem' in request.FILES:
                arquivo = request.FILES['imagem']
                pasta = 'produtos_roupa'
                filename = default_storage.save(f'{pasta}/{arquivo.name}', arquivo)
                produto.imagem = filename
            
            produto.save()
            
            return redirect('servicos:produtos_lista')
        
        # GET - mostrar formulário
        categorias = CategoriaRoupa.objects(ativo=True).order_by('nome')
        
        context = {
            'produto': produto,
            'categorias': categorias,
            'page_title': f'{"Editar" if produto else "Novo"} Produto'
        }
        
        return render(request, 'servicos/roupas/produto_form.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao processar produto: {str(e)}")
        return redirect('servicos:produtos_lista')

@login_required
@staff_required
def produto_delete(request, pk):
    """Deleta um produto de roupa"""
    try:
        produto = ProdutoRoupa.objects.get(id=pk)
        produto.delete()
        
        return redirect('servicos:produtos_lista')
        
    except Exception as e:
        print(f"❌ Erro ao deletar produto: {str(e)}")
        return redirect('servicos:produtos_lista')

# ============================================
# VIEWS PARA VENDAS
# ============================================

@login_required
@staff_required
def vendas_lista(request):
    """Lista todas as vendas"""
    try:
        # Filtros
        status = request.GET.get('status', '')
        data_inicio = request.GET.get('data_inicio', '')
        data_fim = request.GET.get('data_fim', '')
        
        # Buscar vendas
        vendas = VendaRoupa.objects.all()
        
        if status:
            vendas = vendas.filter(status=status)
        
        if data_inicio and data_fim:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            fim = datetime.strptime(data_fim, '%Y-%m-%d')
            vendas = vendas.filter(data_venda__gte=inicio, data_venda__lte=fim)
        
        # Ordenar por data
        vendas = sorted(vendas, key=lambda x: x.data_venda, reverse=True)
        
        # Paginação
        paginator = Paginator(vendas, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        total_vendas = len(vendas)
        vendas_hoje = VendaRoupa.vendas_hoje()
        total_hoje = sum(float(v.valor_total) for v in vendas_hoje)
        
        context = {
            'vendas': page_obj,
            'total_vendas': total_vendas,
            'total_hoje': total_hoje,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'page_title': 'Vendas de Roupa'
        }
        
        return render(request, 'servicos/roupas/vendas_lista.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao listar vendas: {str(e)}")
        return render(request, 'servicos/roupas/vendas_lista.html', {
            'vendas': [],
            'page_title': 'Vendas de Roupa'
        })

@login_required
@staff_required
def venda_nova(request):
    """Cria uma nova venda"""
    try:
        if request.method == 'POST':
            # Processar venda
            cliente_nome = request.POST.get('cliente_nome')
            cliente_telefone = request.POST.get('cliente_telefone', '')
            cliente_email = request.POST.get('cliente_email', '')
            
            # Gerar número da venda
            numero_venda = VendaRoupa.gerar_numero_venda()
            
            # Processar itens (recebidos como JSON)
            itens_json = request.POST.get('itens', '[]')
            itens = json.loads(itens_json)
            
            # Calcular valores
            subtotal = sum(float(item['preco_total']) for item in itens)
            desconto = float(request.POST.get('desconto', 0))
            valor_total = subtotal - desconto
            
            # Criar venda
            venda = VendaRoupa(
                numero_venda=numero_venda,
                cliente_nome=cliente_nome,
                cliente_telefone=cliente_telefone,
                cliente_email=cliente_email,
                itens=itens,
                subtotal=subtotal,
                desconto=desconto,
                valor_total=valor_total,
                forma_pagamento=request.POST.get('forma_pagamento', 'dinheiro'),
                observacoes=request.POST.get('observacoes', ''),
                vendedor=request.user.username if request.user else ''
            )
            
            # Atualizar estoque
            for item in itens:
                produto = ProdutoRoupa.objects.get(id=item['produto_id'])
                tamanho = item['tamanho']
                quantidade = int(item['quantidade'])
                
                # Atualizar estoque por tamanho
                if tamanho == 'PP':
                    produto.estoque_pp = max(0, produto.estoque_pp - quantidade)
                elif tamanho == 'P':
                    produto.estoque_p = max(0, produto.estoque_p - quantidade)
                elif tamanho == 'M':
                    produto.estoque_m = max(0, produto.estoque_m - quantidade)
                elif tamanho == 'G':
                    produto.estoque_g = max(0, produto.estoque_g - quantidade)
                elif tamanho == 'GG':
                    produto.estoque_gg = max(0, produto.estoque_gg - quantidade)
                
                produto.save()
            
            venda.save()
            
            return JsonResponse({
                'success': True,
                'venda_id': str(venda.id),
                'numero_venda': venda.numero_venda
            })
        
        # GET - mostrar formulário
        produtos = ProdutoRoupa.objects(ativo=True).order_by('categoria', 'nome')
        
        context = {
            'produtos': produtos,
            'page_title': 'Nova Venda'
        }
        
        return render(request, 'servicos/roupas/venda_form.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao criar venda: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@staff_required
def venda_detalhe(request, pk):
    """Visualiza detalhes de uma venda"""
    try:
        venda = VendaRoupa.objects.get(id=pk)
        
        # Buscar informações dos produtos
        produtos_detalhe = []
        for item in venda.itens:
            produto_id = item.get('produto_id')
            try:
                produto = ProdutoRoupa.objects.get(id=produto_id)
                produtos_detalhe.append({
                    'produto': produto,
                    'tamanho': item.get('tamanho'),
                    'quantidade': item.get('quantidade'),
                    'preco_unitario': item.get('preco_unitario'),
                    'preco_total': item.get('preco_total'),
                })
            except:
                pass
        
        context = {
            'venda': venda,
            'produtos_detalhe': produtos_detalhe,
            'page_title': f'Venda #{venda.numero_venda}'
        }
        
        return render(request, 'servicos/roupas/venda_detalhe.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao visualizar venda: {str(e)}")
        return redirect('servicos:vendas_lista')

@login_required
@staff_required
def categorias_lista(request):
    """Lista todas as categorias de roupa"""
    try:
        categorias = CategoriaRoupa.objects.all().order_by('nome')
        
        # Estatísticas por categoria
        stats = {}
        for cat in categorias:
            total_produtos = ProdutoRoupa.objects(categoria=cat).count()
            produtos_ativos = ProdutoRoupa.objects(categoria=cat, ativo=True).count()
            stats[str(cat.id)] = {
                'total': total_produtos,
                'ativos': produtos_ativos
            }
        
        context = {
            'categorias': categorias,
            'stats': stats,
            'page_title': 'Categorias de Roupa'
        }
        
        return render(request, 'servicos/roupas/categorias_lista.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao listar categorias: {str(e)}")
        return render(request, 'servicos/roupas/categorias_lista.html', {
            'categorias': [],
            'page_title': 'Categorias de Roupa'
        })

@login_required
@staff_required
def categoria_form(request, pk=None):
    """Cria ou edita uma categoria"""
    try:
        categoria = None
        if pk:
            categoria = CategoriaRoupa.objects.get(id=pk)
        
        if request.method == 'POST':
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            ativo = request.POST.get('ativo') == 'on'
            
            if not categoria:
                categoria = CategoriaRoupa(
                    nome=nome,
                    descricao=descricao,
                    ativo=ativo
                )
            else:
                categoria.nome = nome
                categoria.descricao = descricao
                categoria.ativo = ativo
            
            categoria.save()
            
            return redirect('servicos:categorias_lista')
        
        context = {
            'categoria': categoria,
            'page_title': f'{"Editar" if categoria else "Nova"} Categoria'
        }
        
        return render(request, 'servicos/roupas/categoria_form.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao processar categoria: {str(e)}")
        return redirect('servicos:categorias_lista')

@login_required
@staff_required
def estoque_controle(request):
    """Página de controle de estoque"""
    try:
        produtos = ProdutoRoupa.objects(ativo=True)
        
        # Produtos com estoque baixo
        estoque_baixo = [p for p in produtos if p.estoque_baixo]
        
        # Estatísticas
        total_produtos = len(produtos)
        total_estoque = sum(p.estoque_total for p in produtos)
        valor_total_estoque = sum(p.estoque_total * float(p.preco) for p in produtos)
        
        context = {
            'produtos': produtos,
            'estoque_baixo': estoque_baixo,
            'total_produtos': total_produtos,
            'total_estoque': total_estoque,
            'valor_total_estoque': valor_total_estoque,
            'page_title': 'Controle de Estoque'
        }
        
        return render(request, 'servicos/roupas/estoque_controle.html', context)
        
    except Exception as e:
        print(f"❌ Erro ao visualizar estoque: {str(e)}")
        return render(request, 'servicos/roupas/estoque_controle.html', {
            'produtos': [],
            'page_title': 'Controle de Estoque'
        })

