from django.db import models
from api.unidade.models import Unidade

class Acordo(models.Model):
    valor_total = models.FloatField()
    numero_parcelas = models.IntegerField()
    data_criacao = models.DateTimeField()
    status_acordo = models.BooleanField(default=True)
    id_unidade = models.ForeignKey(Unidade, on_delete=models.SET_NULL, null=True, related_name='acordo')
    
    class Meta:
        db_table = 'Acordo'
        verbose_name = 'Acordo'
        verbose_name_plural = 'Acordos'
        
    def __str__(self):
        return f'{self.valor_total} ({self.numero_parcelas})'
    
class Acordo_Parcela(models.Model):
    
    STATUS_CHOICES = [
        ("Pago","PAGO"),
        ("Pendente","PENDENTE"),
        ("Atrasada","ATRASADA"),
        ("Cancelada","CANCELADA")
    ]
    
    numero_parcela = models.IntegerField()
    valor_parcela = models.FloatField()
    data_vencimento = models.DateTimeField()
    data_pagamento = models.DateTimeField()
    multa = models.DecimalField(max_digits=10, decimal_places=2)
    juros = models.DecimalField(max_digits=10, decimal_places=2)
    status_parcela = models.CharField(max_length=50, choices=STATUS_CHOICES)
    
    
    

