from django.db import models
from api.condominio.models import Condominio
from api.usuarios.models import Usuario

class Unidade(models.Model):
    
    STATUS_CHOICES = [
        ('Ocupado', 'OCUPADO'),
        ('Disponivel','DISPONIVEL')
    ]
    
    numero = models.CharField(max_length=5)
    bloco = models.CharField(max_length=10)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    condominio = models.ForeignKey(Condominio, on_delete=models.SET_NULL, null=True, related_name='unidades')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='unidades')
    
    class Meta:
        db_table = 'Unidade'
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return f'{self.bloco}{self.numero} ({self.status})'