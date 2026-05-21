from django.db import models

class Condominio(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=14)
    endereco = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Condominios'
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'

    def __str__(self):
        return f'{self.nome} ({self.cnpj})'
