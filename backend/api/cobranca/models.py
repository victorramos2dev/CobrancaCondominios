from django.db import models
from api.unidade.models import Unidade
from api.acordo.models import Acordo
from api.condominio.models import Condominio

class Cobranca(models.Model):
    competencia = models.DateTimeField()
    data_vencimento = models.DateTimeField()
    valor = models.FloatField()
    data_pagamento = models.DateTimeField()
    forma_pagamento = models.CharField(max_length=45)
    multa = models.DecimalField(max_digits=10, decimal_places=2)
    juros = models.DecimalField(max_digits=10, decimal_places=2)
    id_unidade = models.ForeignKey(Unidade, on_delete=models.SET_NULL, null=True, related_name='cobranca_unidade')
    id_acordo = models.ForeignKey(Acordo, on_delete=models.CASCADE,related_name='cobranca_acordo')
    
    class Meta:
        db_table = 'Cobranca'
        verbose_name = 'Cobranca'
        verbose_name_plural = 'Cobrancas'
    
    def __str__(self):
        return f'{self.data_vencimento} ({self.valor})'

class ConfiguracaoMulta(models.Model):
    multa = models.DecimalField(max_digits=10, decimal_places=2)
    juros = models.DecimalField(max_digits=10, decimal_places=2)
    id_condominio = models.ForeignKey(Condominio, on_delete=models.SET_NULL, related_name='multa')
    
    class Meta:
        db_table = 'ConfiguracaoMulta'
        verbose_name = 'ConfiguracaoMulta'
        verbose_name_plural = 'ConfiguracaoMultas'
    
    def __str__(self):
        return f'{self.multa} ({self.juros})'
