from django.db import models
from api.cobranca.models import Cobranca

class HistoricoStatus(models.Model):
    status_anterior = models.CharField(max_length=45)
    status_novo = models.CharField(max_length=45)
    data_alteracao = models.DateTimeField()
    id_cobranca = models.ForeignKey(Cobranca, on_delete=models.SET_NULL, related_name='historico')
    
    class Meta:
        db_table = 'Historico'
        verbose_name = 'Historico'
        verbose_name_plural = 'Historicos'
    
    def __str__(self):
        return f'{self.status_anterior} ({self.status_novo})'
