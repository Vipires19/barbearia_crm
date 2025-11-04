"""
Modelos MongoDB para a barbearia
"""
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
from django.utils import timezone


class HorarioDisponibilidadeMongo(EmbeddedDocument):
    """Horários disponíveis dos profissionais"""
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    dia_semana = fields.IntField(choices=DIAS_SEMANA, required=True)
    hora_inicio = fields.StringField(required=True)  # Formato "08:00"
    hora_fim = fields.StringField(required=True)    # Formato "18:00"
    intervalo_minutos = fields.IntField(default=30)
    ativo = fields.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"


class ProfissionalMongo(Document):
    """Profissionais da barbearia"""
    nome_completo = fields.StringField(max_length=200, required=True)
    username = fields.StringField(max_length=150, unique=True, required=True)
    email = fields.EmailField()
    telefone = fields.StringField(max_length=20)
    bio = fields.StringField()
    foto = fields.StringField()  # Caminho da imagem
    experiencia_anos = fields.IntField(default=0)
    avaliacao_media = fields.FloatField(default=5.0)
    total_avaliacoes = fields.IntField(default=0)
    ativo = fields.BooleanField(default=True)
    
    # Especialidades (lista de strings)
    especialidades = fields.ListField(fields.StringField())
    
    # Horários de disponibilidade
    horarios_disponibilidade = fields.ListField(fields.EmbeddedDocumentField(HorarioDisponibilidadeMongo))
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'profissionais',
        'indexes': ['username', 'email', 'ativo']
    }
    
    def __str__(self):
        return self.nome_completo


class CategoriaServicoMongo(Document):
    """Categoria dos serviços oferecidos pela barbearia"""
    nome = fields.StringField(max_length=100, unique=True, required=True)
    descricao = fields.StringField()
    ativo = fields.BooleanField(default=True)
    ordem = fields.IntField(default=0)
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'categorias_servicos',
        'indexes': ['nome', 'ativo', 'ordem']
    }
    
    def __str__(self):
        return self.nome


class ServicoMongo(Document):
    """Serviços oferecidos pela barbearia"""
    DURACAO_CHOICES = [
        (15, '15 minutos'),
        (30, '30 minutos'),
        (45, '45 minutos'),
        (60, '1 hora'),
        (90, '1h30'),
        (120, '2 horas'),
    ]
    
    nome = fields.StringField(max_length=200, required=True)
    descricao = fields.StringField()
    categoria_id = fields.StringField(required=True)  # ID da categoria
    preco = fields.FloatField(required=True)
    duracao = fields.IntField(choices=DURACAO_CHOICES, default=30)
    ativo = fields.BooleanField(default=True)
    imagem = fields.StringField()  # Caminho da imagem
    ordem = fields.IntField(default=0)
    
    # Profissionais habilitados (lista de IDs)
    profissionais_habilitados = fields.ListField(fields.StringField())
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'servicos',
        'indexes': ['nome', 'categoria_id', 'ativo', 'ordem']
    }
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"


class AgendamentoMongo(Document):
    """Agendamentos dos clientes"""
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('falta', 'Falta'),
    ]
    
    # Dados do cliente
    cliente_nome = fields.StringField(max_length=200, required=True)
    cliente_telefone = fields.StringField(max_length=20, required=True)
    cliente_email = fields.EmailField()
    
    # Dados do agendamento
    profissional_id = fields.StringField(required=True)
    servico_id = fields.StringField(required=True)
    data_agendamento = fields.StringField(required=True)  # Formato "YYYY-MM-DD"
    hora_agendamento = fields.StringField(required=True)  # Formato "HH:MM"
    status = fields.StringField(choices=STATUS_CHOICES, default='agendado')
    observacoes = fields.StringField()
    valor_total = fields.FloatField(required=True)
    
    # Integração WhatsApp
    confirmado_whatsapp = fields.BooleanField(default=False)
    whatsapp_id = fields.StringField()
    mensagem_confirmacao = fields.StringField()
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'agendamentos',
        'indexes': [
            'profissional_id', 'data_agendamento', 'status',
            'cliente_telefone', 'data_criacao'
        ]
    }
    
    def __str__(self):
        return f"{self.cliente_nome} - {self.data_agendamento} {self.hora_agendamento}"


class AvaliacaoMongo(Document):
    """Avaliações dos clientes sobre os serviços"""
    agendamento_id = fields.StringField(required=True)
    nota = fields.IntField(min_value=1, max_value=5, required=True)
    comentario = fields.StringField()
    data_avaliacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'avaliacoes',
        'indexes': ['agendamento_id', 'data_avaliacao']
    }
    
    def __str__(self):
        return f"Avaliação - {self.nota} estrelas"


class ConfiguracaoBarbeariaMongo(Document):
    """Configurações gerais da barbearia"""
    nome_barbearia = fields.StringField(max_length=200, default="Barbearia")
    telefone = fields.StringField(max_length=20)
    endereco = fields.StringField()
    horario_funcionamento = fields.StringField()
    whatsapp_business_id = fields.StringField()
    token_whatsapp = fields.StringField()
    mongo_connection_string = fields.StringField()
    ativo = fields.BooleanField(default=True)
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'configuracao_barbearia'
    }
    
    def __str__(self):
        return self.nome_barbearia


class ClienteMongo(Document):
    """Cliente da barbearia - para agilizar agendamentos"""
    nome = fields.StringField(max_length=200, required=True)
    telefone = fields.StringField(max_length=20, required=True, unique=True)
    email = fields.EmailField()
    cpf = fields.StringField(max_length=14)
    data_nascimento = fields.DateTimeField()
    
    # Endereço
    endereco = fields.StringField()
    cidade = fields.StringField()
    cep = fields.StringField()
    
    # Preferências
    profissional_preferido = fields.StringField()  # ID do profissional
    observacoes = fields.StringField()
    
    # Estatísticas
    total_agendamentos = fields.IntField(default=0)
    total_compras = fields.IntField(default=0)
    valor_total_gasto = fields.FloatField(default=0)
    ultimo_agendamento = fields.DateTimeField()
    ultima_compra = fields.DateTimeField()
    
    # Flags
    cliente_frequente = fields.BooleanField(default=False)
    notificacoes_whatsapp = fields.BooleanField(default=True)
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'clientes',
        'indexes': ['telefone', 'email', 'cpf', 'cliente_frequente']
    }
    
    def __str__(self):
        return f"{self.nome} ({self.telefone})"
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas do cliente"""
        try:
            from .models import VendaRoupa
            from .models_mongo import AgendamentoMongo
            
            # Contar vendas
            vendas = VendaRoupa.objects(cliente_telefone=self.telefone)
            self.total_compras = vendas.count()
            self.valor_total_gasto = sum(float(v.valor_total) for v in vendas)
            
            # Contar agendamentos
            agendamentos = AgendamentoMongo.objects(cliente_telefone=self.telefone)
            self.total_agendamentos = agendamentos.count()
            
            # Última compra
            ultima_venda = vendas.order_by('-data_venda').first()
            if ultima_venda:
                self.ultima_compra = ultima_venda.data_venda
            
            # Último agendamento
            ultimo_agend = agendamentos.order_by('-data_criacao').first()
            if ultimo_agend:
                self.ultimo_agendamento = ultimo_agend.data_criacao
            
            # Marcar como frequente se tiver mais de 5 agendamentos/compras
            self.cliente_frequente = (self.total_agendamentos + self.total_compras) >= 5
            
            self.save()
        except Exception as e:
            print(f"⚠️ Erro ao atualizar estatísticas do cliente: {e}")
            pass


class AgendaDiaMongo(Document):
    """Agenda do dia - visão consolidada dos agendamentos"""
    data = fields.DateTimeField(required=True)
    profissional_id = fields.StringField(required=True)
    profissional_nome = fields.StringField()
    
    # Agendamentos do dia
    agendamentos = fields.ListField(fields.DictField())
    
    # Estatísticas do dia
    total_agendamentos = fields.IntField(default=0)
    total_concluidos = fields.IntField(default=0)
    total_cancelados = fields.IntField(default=0)
    receita_total = fields.FloatField(default=0)
    
    # Horários ocupados
    horarios_ocupados = fields.ListField(fields.StringField())  # ["08:00", "09:00", ...]
    horarios_disponiveis = fields.ListField(fields.StringField())  # ["10:00", "14:00", ...]
    
    # Campos de auditoria
    data_criacao = fields.DateTimeField(default=datetime.now)
    data_atualizacao = fields.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'agenda_dia',
        'indexes': [
            ('data', 'profissional_id'),
            'data',
            'profissional_id'
        ]
    }
    
    def __str__(self):
        return f"Agenda {self.data.strftime('%d/%m/%Y')} - {self.profissional_nome}"
    
    @classmethod
    def criar_agenda_do_dia(cls, data, profissional_id):
        """Cria ou atualiza a agenda do dia"""
        from .models_mongo import AgendamentoMongo
        
        # Buscar ou criar agenda
        agenda, created = cls.objects.get_or_create(
            data=data,
            profissional_id=profissional_id
        )
        
        # Buscar agendamentos do dia
        agendamentos = AgendamentoMongo.objects(
            data_agendamento=data.strftime('%Y-%m-%d'),
            profissional_id=profissional_id
        )
        
        # Atualizar agenda
        agenda.total_agendamentos = agendamentos.count()
        agenda.total_concluidos = agendamentos.filter(status='concluido').count()
        agenda.total_cancelados = agendamentos.filter(status='cancelado').count()
        agenda.receita_total = sum(a.valor_total for a in agendamentos.filter(status='concluido'))
        agenda.agendamentos = [
            {
                'id': str(a.id),
                'cliente': a.cliente_nome,
                'hora': a.hora_agendamento,
                'servico': a.servico_id,
                'status': a.status,
                'valor': a.valor_total
            }
            for a in agendamentos
        ]
        
        # Horários ocupados
        agenda.horarios_ocupados = [a.hora_agendamento for a in agendamentos]
        
        # Calcular horários disponíveis (precisa das regras de disponibilidade)
        # Por enquanto, retorna horários vazios
        agenda.horarios_disponiveis = []
        
        agenda.save()
        return agenda
