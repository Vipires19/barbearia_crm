"""
Comando para popular produtos de vestuário de exemplo
"""
from django.core.management.base import BaseCommand
from servicos.models import ProdutoRoupa


class Command(BaseCommand):
    help = 'Cria produtos de vestuário de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('🎯 Criando produtos de vestuário de exemplo...')
        
        # Produtos de exemplo
        produtos = [
            {
                'nome': 'Camiseta Básica Preta',
                'categoria': 'Camisetas',
                'preco': 29.90,
                'preco_custo': 15.00,
                'estoque_pp': 5,
                'estoque_p': 10,
                'estoque_m': 20,
                'estoque_g': 15,
                'estoque_gg': 5,
                'marca': 'Básico',
                'cor': 'Preta',
                'material': 'Algodão'
            },
            {
                'nome': 'Camiseta Básica Branca',
                'categoria': 'Camisetas',
                'preco': 29.90,
                'preco_custo': 15.00,
                'estoque_pp': 3,
                'estoque_p': 12,
                'estoque_m': 25,
                'estoque_g': 18,
                'estoque_gg': 7,
                'marca': 'Básico',
                'cor': 'Branca',
                'material': 'Algodão'
            },
            {
                'nome': 'Boné Aba Reta',
                'categoria': 'Bonés',
                'preco': 35.00,
                'preco_custo': 18.00,
                'estoque_pp': 0,
                'estoque_p': 0,
                'estoque_m': 0,
                'estoque_g': 0,
                'estoque_gg': 0,
                'estoque_total': 15,  # Boné tamanho único
                'marca': 'Street',
                'cor': 'Preto',
                'material': 'Algodão'
            },
            {
                'nome': 'Short Esportivo',
                'categoria': 'Shorts',
                'preco': 45.90,
                'preco_custo': 22.00,
                'estoque_pp': 0,
                'estoque_p': 8,
                'estoque_m': 15,
                'estoque_g': 12,
                'estoque_gg': 5,
                'marca': 'Sports',
                'cor': 'Preto',
                'material': 'Polyester'
            },
            {
                'nome': 'Meia Esportiva',
                'categoria': 'Meias',
                'preco': 15.90,
                'preco_custo': 5.00,
                'estoque_total': 50,  # Meia tamanho único
                'marca': 'Sports',
                'cor': 'Branca',
                'material': 'Algodão'
            }
        ]
        
        criados = 0
        for dados in produtos:
            try:
                # Verificar se já existe
                produto = ProdutoRoupa.objects(nome=dados['nome']).first()
                if produto:
                    self.stdout.write(f'⏭️  Produto "{dados["nome"]}" já existe, pulando...')
                    continue
                
                # Criar novo produto
                produto = ProdutoRoupa(**dados)
                produto.save()
                criados += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Produto "{dados["nome"]}" criado!'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao criar "{dados["nome"]}": {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Total: {criados} produtos criados com sucesso!'))
        self.stdout.write('\n💡 Agora você pode acessar /servicos/vestuario/ para ver os produtos')




