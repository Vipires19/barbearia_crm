from django.db import models
from mongoengine import Document, EmbeddedDocument, fields
from django.urls import reverse
from datetime import datetime
import os
from django.core.files.storage import default_storage
from django.conf import settings

# Create your models here.

class Profissional(Document):
    """
    Documento que representa um profissional da barbearia
    """
    nome_completo = fields.StringField(max_length=200, required=True, verbose_name="Nome Completo")
    telefone = fields.StringField(max_length=20, verbose_name="Telefone")
    email = fields.EmailField(required=False, verbose_name="E-mail")
    foto = fields.StringField(verbose_name="Caminho da Foto")
    bio = fields.StringField(verbose_name="Biografia")
    especialidades = fields.ListField(fields.StringField(max_length=100), verbose_name="Especialidades")
    experiencia_anos = fields.IntField(min_value=0, default=0, verbose_name="Experiência (anos)")
    ativo = fields.BooleanField(default=True, verbose_name="Ativo")
    data_contratacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Contratação")
    avaliacao_media = fields.FloatField(default=0.0, verbose_name="Avaliação Média")
    total_avaliacoes = fields.IntField(default=0, verbose_name="Total de Avaliações")
    
    # Configurações do documento
    meta = {
        'collection': 'profissionais',
        'ordering': ['nome_completo'],
        'indexes': [
            'nome_completo',
            'ativo',
            'especialidades',
        ]
    }
    
    def __str__(self):
        return self.nome_completo

class Servico(Document):
    """
    Documento principal que representa um serviço da barbearia
    """
    # Campos básicos do serviço
    nome = fields.StringField(max_length=200, required=True, verbose_name="Nome do Serviço")
    descricao = fields.StringField(verbose_name="Descrição")
    preco = fields.DecimalField(min_value=0, precision=2, required=True, verbose_name="Preço")
    categoria = fields.StringField(max_length=100, required=True, verbose_name="Categoria")
    
    # Campo para imagem (armazena o caminho do arquivo)
    imagem = fields.StringField(verbose_name="Caminho da Imagem")
    
    # Status e controle
    disponivel = fields.BooleanField(default=True, verbose_name="Disponível")
    destaque = fields.BooleanField(default=False, verbose_name="Serviço em Destaque")
    
    # Profissionais que podem realizar o serviço
    profissionais_habilitados = fields.ListField(fields.ReferenceField(Profissional), verbose_name="Profissionais Habilitados")
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    data_atualizacao = fields.DateTimeField(default=datetime.now, verbose_name="Última Atualização")
    
    # Campos extras que podem ser úteis (flexibilidade do MongoDB)
    tags = fields.ListField(fields.StringField(max_length=50), verbose_name="Tags")
    duracao_minutos = fields.IntField(min_value=0, default=30, verbose_name="Duração (minutos)")
    materiais_necessarios = fields.ListField(fields.StringField(max_length=100), verbose_name="Materiais Necessários")
    
    # Configurações do documento
    meta = {
        'collection': 'servicos',
        'ordering': ['categoria', 'nome'],
        'indexes': [
            'nome',
            'categoria',
            'disponivel',
            ('categoria', 'nome'),
        ]
    }
    
    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        """Retorna a URL para a página de detalhes do serviço"""
        return reverse('servico_detalhe', kwargs={'servico_id': str(self.id)})
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar a data de modificação
        """
        self.data_atualizacao = datetime.now()
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_categorias(cls):
        """
        Método de classe para buscar todas as categorias disponíveis
        """
        pipeline = [
            {"$match": {"disponivel": True}},
            {"$group": {"_id": "$categoria"}},
            {"$sort": {"_id": 1}}
        ]
        
        result = cls.objects.aggregate(pipeline)
        return [item['_id'] for item in result]
    
    @classmethod
    def buscar_servicos(cls, termo_busca=None, categoria=None, apenas_disponiveis=True):
        """
        Método para busca avançada de serviços
        """
        query = {}
        
        # Filtro por disponibilidade
        if apenas_disponiveis:
            query['disponivel'] = True
        
        # Filtro por categoria
        if categoria:
            query['categoria'] = categoria
        
        # Busca por termo
        if termo_busca:
            # Busca em nome, descrição e tags
            query['$or'] = [
                {'nome': {'$regex': termo_busca, '$options': 'i'}},
                {'descricao': {'$regex': termo_busca, '$options': 'i'}},
                {'tags': {'$in': [termo_busca]}},
                {'categoria': {'$regex': termo_busca, '$options': 'i'}}
            ]
        
        return cls.objects(__raw__=query)

class Agendamento(Document):
    """
    Documento que representa um agendamento
    """
    # Dados do cliente
    cliente_nome = fields.StringField(max_length=200, required=True, verbose_name="Nome do Cliente")
    cliente_telefone = fields.StringField(max_length=20, required=True, verbose_name="Telefone do Cliente")
    cliente_email = fields.EmailField(required=False, verbose_name="E-mail do Cliente")
    
    # Dados do agendamento
    servico = fields.ReferenceField(Servico, required=True, verbose_name="Serviço")
    profissional = fields.ReferenceField(Profissional, required=True, verbose_name="Profissional")
    data_agendamento = fields.DateTimeField(required=True, verbose_name="Data do Agendamento")
    hora_agendamento = fields.StringField(max_length=5, required=True, verbose_name="Hora do Agendamento")
    
    # Status e controle
    status = fields.StringField(
        choices=[
            ('pendente', 'Pendente'),
            ('confirmado', 'Confirmado'),
            ('em_andamento', 'Em Andamento'),
            ('concluido', 'Concluído'),
            ('cancelado', 'Cancelado'),
            ('falta', 'Falta'),
        ],
        default='pendente',
        verbose_name="Status"
    )
    
    # Campos adicionais
    observacoes = fields.StringField(verbose_name="Observações")
    valor_total = fields.DecimalField(min_value=0, precision=2, required=True, verbose_name="Valor Total")
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    data_atualizacao = fields.DateTimeField(default=datetime.now, verbose_name="Última Atualização")
    
    # Campos para WhatsApp
    confirmado_whatsapp = fields.BooleanField(default=False, verbose_name="Confirmado via WhatsApp")
    whatsapp_id = fields.StringField(max_length=100, verbose_name="ID do WhatsApp")
    mensagem_confirmacao = fields.StringField(verbose_name="Mensagem de Confirmação")
    
    # Configurações do documento
    meta = {
        'collection': 'agendamentos',
        'ordering': ['-data_agendamento'],
        'indexes': [
            'cliente_telefone',
            'status',
            'data_agendamento',
            'profissional',
            ('status', 'data_agendamento'),
        ]
    }
    
    def __str__(self):
        return f"{self.cliente_nome} - {self.servico.nome} - {self.data_agendamento.strftime('%d/%m/%Y')} {self.hora_agendamento}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar a data de modificação
        """
        self.data_atualizacao = datetime.now()
        return super().save(*args, **kwargs)

class HorarioDisponivel(Document):
    """
    Documento que representa horários disponíveis de um profissional
    """
    profissional = fields.ReferenceField(Profissional, required=True, verbose_name="Profissional")
    data = fields.DateField(required=True, verbose_name="Data")
    hora_inicio = fields.StringField(max_length=5, required=True, verbose_name="Hora de Início")
    hora_fim = fields.StringField(max_length=5, required=True, verbose_name="Hora de Fim")
    disponivel = fields.BooleanField(default=True, verbose_name="Disponível")
    observacoes = fields.StringField(verbose_name="Observações")
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    data_atualizacao = fields.DateTimeField(default=datetime.now, verbose_name="Última Atualização")
    
    # Configurações do documento
    meta = {
        'collection': 'horarios_disponiveis',
        'ordering': ['data', 'hora_inicio'],
        'indexes': [
            'profissional',
            'data',
            'disponivel',
            ('profissional', 'data'),
        ]
    }
    
    def __str__(self):
        return f"{self.profissional.nome_completo} - {self.data.strftime('%d/%m/%Y')} {self.hora_inicio}-{self.hora_fim}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar a data de modificação
        """
        self.data_atualizacao = datetime.now()
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_horarios_disponiveis(cls, profissional, data):
        """
        Retorna horários disponíveis de um profissional em uma data específica
        """
        return cls.objects(
            profissional=profissional,
            data=data,
            disponivel=True
        ).order_by('hora_inicio')
    
    @classmethod
    def criar_horarios_diarios(cls, profissional, data, hora_inicio, hora_fim, intervalo_minutos=30):
        """
        Cria horários disponíveis para um dia inteiro
        """
        from datetime import datetime, timedelta
        
        # Converter strings de hora para datetime
        inicio = datetime.strptime(hora_inicio, '%H:%M')
        fim = datetime.strptime(hora_fim, '%H:%M')
        
        horarios_criados = []
        horario_atual = inicio
        
        while horario_atual < fim:
            proximo_horario = horario_atual + timedelta(minutes=intervalo_minutos)
            
            if proximo_horario <= fim:
                horario = cls(
                    profissional=profissional,
                    data=data,
                    hora_inicio=horario_atual.strftime('%H:%M'),
                    hora_fim=proximo_horario.strftime('%H:%M'),
                    disponivel=True
                )
                horario.save()
                horarios_criados.append(horario)
            
            horario_atual = proximo_horario
        
        return horarios_criados

class ConfiguracaoBarbearia(Document):
    """
    Documento para configurações da barbearia
    """
    nome_barbearia = fields.StringField(max_length=200, default="Barbearia", verbose_name="Nome da Barbearia")
    telefone = fields.StringField(max_length=20, verbose_name="Telefone")
    endereco = fields.StringField(verbose_name="Endereço")
    horario_funcionamento = fields.StringField(verbose_name="Horário de Funcionamento")
    
    # Configurações de WhatsApp
    whatsapp_business_id = fields.StringField(max_length=100, verbose_name="ID do WhatsApp Business")
    token_whatsapp = fields.StringField(max_length=500, verbose_name="Token do WhatsApp")
    
    # Status da barbearia
    aberta = fields.BooleanField(default=True, verbose_name="Barbearia Aberta")
    ativo = fields.BooleanField(default=True, verbose_name="Ativo")
    
    # Configurações do documento
    meta = {
        'collection': 'configuracao_barbearia',
        'indexes': [
            'ativo',
        ]
    }
    
    def __str__(self):
        return self.nome_barbearia
    
    @classmethod
    def get_configuracao(cls):
        """
        Retorna a configuração da barbearia
        """
        try:
            return cls.objects(ativo=True).first()
        except:
            return cls(
                nome_barbearia="Barbearia",
                ativo=True
            ).save()
    
    @property
    def esta_funcionando(self):
        """
        Verifica se a barbearia está funcionando
        """
        return self.aberta and self.ativo

# ============================================
# MODELOS PARA LOJA DE ROUPAS
# ============================================

class CategoriaRoupa(Document):
    """
    Documento que representa uma categoria de roupa
    """
    nome = fields.StringField(max_length=100, required=True, verbose_name="Nome da Categoria")
    descricao = fields.StringField(verbose_name="Descrição")
    ativo = fields.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    
    meta = {
        'collection': 'categorias_roupa',
        'ordering': ['nome'],
        'indexes': ['nome', 'ativo']
    }
    
    def __str__(self):
        return self.nome

class ProdutoRoupa(Document):
    """
    Documento que representa um produto de roupa
    """
    nome = fields.StringField(max_length=200, required=True, verbose_name="Nome do Produto")
    descricao = fields.StringField(verbose_name="Descrição")
    categoria = fields.StringField(max_length=100, verbose_name="Categoria")
    
    # Informações do produto
    preco = fields.DecimalField(min_value=0, precision=2, required=True, verbose_name="Preço")
    preco_custo = fields.DecimalField(min_value=0, precision=2, verbose_name="Preço de Custo")
    
    # Controle de estoque
    estoque_total = fields.IntField(default=0, verbose_name="Estoque Total")
    estoque_minimo = fields.IntField(default=5, verbose_name="Estoque Mínimo")
    
    # Tamanhos disponíveis (campos numéricos separados)
    estoque_pp = fields.IntField(default=0, verbose_name="Estoque PP")
    estoque_p = fields.IntField(default=0, verbose_name="Estoque P")
    estoque_m = fields.IntField(default=0, verbose_name="Estoque M")
    estoque_g = fields.IntField(default=0, verbose_name="Estoque G")
    estoque_gg = fields.IntField(default=0, verbose_name="Estoque GG")
    
    # Dados do produto
    marca = fields.StringField(max_length=100, verbose_name="Marca")
    cor = fields.StringField(max_length=50, verbose_name="Cor")
    material = fields.StringField(max_length=100, verbose_name="Material")
    
    # Campo para imagem
    imagem = fields.StringField(verbose_name="Caminho da Imagem")
    
    # Tags para busca
    tags = fields.ListField(fields.StringField(max_length=50), verbose_name="Tags")
    
    # Status
    ativo = fields.BooleanField(default=True, verbose_name="Ativo")
    em_destaque = fields.BooleanField(default=False, verbose_name="Em Destaque")
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    data_atualizacao = fields.DateTimeField(default=datetime.now, verbose_name="Última Atualização")
    
    meta = {
        'collection': 'produtos_roupa',
        'ordering': ['categoria', 'nome'],
        'indexes': [
            'nome',
            'categoria',
            'ativo',
            'marca',
            ('categoria', 'nome'),
        ]
    }
    
    def __str__(self):
        return f"{self.nome} - {self.categoria if self.categoria else 'Sem Categoria'}"
    
    @property
    def estoque_disponivel_pp(self):
        """Retorna se PP está disponível"""
        return self.estoque_pp > 0
    
    @property
    def estoque_disponivel_p(self):
        """Retorna se P está disponível"""
        return self.estoque_p > 0
    
    @property
    def estoque_disponivel_m(self):
        """Retorna se M está disponível"""
        return self.estoque_m > 0
    
    @property
    def estoque_disponivel_g(self):
        """Retorna se G está disponível"""
        return self.estoque_g > 0
    
    @property
    def estoque_disponivel_gg(self):
        """Retorna se GG está disponível"""
        return self.estoque_gg > 0
    
    @property
    def estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        return self.estoque_total <= self.estoque_minimo
    
    @property
    def margem_lucro(self):
        """Calcula a margem de lucro do produto"""
        if self.preco_custo and self.preco_custo > 0:
            lucro = self.preco - self.preco_custo
            return (lucro / self.preco_custo) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Atualiza o estoque total e a data de atualização"""
        self.estoque_total = self.estoque_pp + self.estoque_p + self.estoque_m + self.estoque_g + self.estoque_gg
        self.data_atualizacao = datetime.now()
        return super().save(*args, **kwargs)
    
    @classmethod
    def buscar_produtos(cls, termo_busca=None, categoria=None, apenas_disponiveis=True):
        """Método para busca avançada de produtos"""
        query = {}
        
        if apenas_disponiveis:
            query['ativo'] = True
        
        if categoria:
            query['categoria'] = categoria
        
        if termo_busca:
            query['$or'] = [
                {'nome': {'$regex': termo_busca, '$options': 'i'}},
                {'marca': {'$regex': termo_busca, '$options': 'i'}},
            ]
        
        return cls.objects(__raw__=query)
    
    @classmethod
    def produtos_estoque_baixo(cls):
        """Retorna produtos com estoque baixo"""
        # No MongoEngine, precisamos fazer a query manualmente
        produtos = cls.objects(ativo=True)
        return [p for p in produtos if p.estoque_total <= p.estoque_minimo]

class VendaRoupa(Document):
    """
    Documento que representa uma venda de roupa
    """
    # Dados da venda
    numero_venda = fields.StringField(max_length=50, unique=True, verbose_name="Número da Venda")
    data_venda = fields.DateTimeField(default=datetime.now, verbose_name="Data da Venda")
    
    # Dados do cliente
    cliente_nome = fields.StringField(max_length=200, required=True, verbose_name="Nome do Cliente")
    cliente_telefone = fields.StringField(max_length=20, verbose_name="Telefone do Cliente")
    cliente_email = fields.EmailField(required=False, verbose_name="E-mail do Cliente")
    
    # Itens da venda
    itens = fields.ListField(
        fields.DictField(),
        verbose_name="Itens da Venda"
    )
    
    # Valores
    subtotal = fields.DecimalField(min_value=0, precision=2, required=True, verbose_name="Subtotal")
    desconto = fields.DecimalField(min_value=0, precision=2, default=0, verbose_name="Desconto")
    valor_total = fields.DecimalField(min_value=0, precision=2, required=True, verbose_name="Valor Total")
    
    # Forma de pagamento
    forma_pagamento = fields.StringField(
        choices=[
            ('dinheiro', 'Dinheiro'),
            ('debito', 'Cartão Débito'),
            ('credito', 'Cartão Crédito'),
            ('pix', 'PIX'),
            ('outro', 'Outro')
        ],
        default='dinheiro',
        verbose_name="Forma de Pagamento"
    )
    
    # Status
    status = fields.StringField(
        choices=[
            ('pendente', 'Pendente'),
            ('concluida', 'Concluída'),
            ('cancelada', 'Cancelada'),
            ('devolvida', 'Devolvida'),
        ],
        default='concluida',
        verbose_name="Status"
    )
    
    # Observações
    observacoes = fields.StringField(verbose_name="Observações")
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now, verbose_name="Data de Criação")
    data_atualizacao = fields.DateTimeField(default=datetime.now, verbose_name="Última Atualização")
    
    # Vendedor (opcional, para registrar quem fez a venda)
    vendedor = fields.StringField(max_length=200, verbose_name="Vendedor")
    
    meta = {
        'collection': 'vendas_roupa',
        'ordering': ['-data_venda'],
        'indexes': [
            'numero_venda',
            'data_venda',
            'cliente_nome',
            'status',
            'forma_pagamento',
            ('data_venda', 'status'),
        ]
    }
    
    def __str__(self):
        return f"Venda #{self.numero_venda} - {self.cliente_nome}"
    
    def save(self, *args, **kwargs):
        """Atualiza a data de modificação"""
        self.data_atualizacao = datetime.now()
        return super().save(*args, **kwargs)
    
    @classmethod
    def gerar_numero_venda(cls):
        """Gera um número único de venda"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Verificar se já existe
        count = cls.objects.filter(numero_venda__contains=timestamp).count()
        numero = f"VENDA-{timestamp}-{count + 1:03d}"
        
        return numero
    
    @classmethod
    def vendas_periodo(cls, data_inicio, data_fim):
        """Retorna vendas em um período específico"""
        return cls.objects(
            data_venda__gte=data_inicio,
            data_venda__lte=data_fim
        ).order_by('-data_venda')
    
    @classmethod
    def vendas_hoje(cls):
        """Retorna vendas do dia atual"""
        from datetime import datetime, timedelta
        hoje = datetime.now().date()
        amanha = hoje + timedelta(days=1)
        
        return cls.objects(
            data_venda__gte=datetime.combine(hoje, datetime.min.time()),
            data_venda__lt=datetime.combine(amanha, datetime.min.time())
        )
    
    @property
    def lucro_bruto(self):
        """Calcula o lucro bruto da venda"""
        # Calcula a diferença entre o valor vendido e o custo dos produtos
        lucro = 0
        for item in self.itens:
            produto_id = item.get('produto_id')
            quantidade = item.get('quantidade', 0)
            preco_venda = item.get('preco_venda', 0)
            
            try:
                produto = ProdutoRoupa.objects.get(id=produto_id)
                if produto.preco_custo:
                    lucro += (preco_venda - float(produto.preco_custo)) * quantidade
            except:
                pass
        
        return lucro