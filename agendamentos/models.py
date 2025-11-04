# agendamentos/models.py
# Este arquivo não precisa de modelos Django ORM
# Todos os modelos estão no MongoDB em servicos/models.py

# Importar apenas para compatibilidade se necessário
from django.db import models

# Placeholder para manter compatibilidade
class PlaceholderModel(models.Model):
    """Modelo placeholder para manter compatibilidade"""
    nome = models.CharField(max_length=100, default="placeholder")
    
    class Meta:
        app_label = 'agendamentos'