from django.db import models
from api.cobranca.models import Cobranca


class HistoricoStatus(models.Model):
    cobranca = models.ForeignKey(
        Cobranca,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name='Cobrança',
    )
    status_anterior = models.CharField(max_length=10, verbose_name='Status Anterior')
    status_novo = models.CharField(max_length=10, verbose_name='Status Novo')
    data_alteracao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Alteração')
    usuario = models.CharField(max_length=150, blank=True, null=True, verbose_name='Usuário')

    class Meta:
        db_table = 'historico_status'
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Históricos de Status'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f'Cobrança {self.cobranca_id}: {self.status_anterior} → {self.status_novo}'
