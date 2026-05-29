from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal


class Condominio(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        db_index=True,
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        verbose_name='CNPJ',
        validators=[RegexValidator(
            regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$',
            message='CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX ou 14 dígitos.'
        )],
    )
    endereco = models.CharField(max_length=200, verbose_name='Endereço')
    status = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'condominios'
        verbose_name = 'Condomínio'
        verbose_name_plural = 'Condomínios'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome}'
    
class ConfiguracaoMulta(models.Model):
    condominio = models.OneToOneField(
        Condominio,
        on_delete=models.CASCADE,
        related_name='configuracao_multa',
        verbose_name='Condominio',
    )
    percentual_multa = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.02'),
        verbose_name='Porcentual de Multa',
        help_text='Ex: 0.02 para 2%',
    )
    percentual_juros_dia = models.DecimalField(
        max_digits=7,
        decimal_places=6,
        default=Decimal('0.00033'),
        verbose_name='Percentual de Juros por Dia',
        help_text='Ex: 0.00033 para 0,033 ao dia',
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'configuracoes_multa'
        verbose_name = 'Configuração de Multa'
        verbose_name_plural = 'Configurações de Multa'
    
    def __str__(self):
        return f'Config multa - {self.condominio.nome}'
