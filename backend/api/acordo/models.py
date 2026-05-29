from django.db import models
from api.unidade.models import Unidade


class Acordo(models.Model):

    STATUS_ATIVO = 'ATIVO'
    STATUS_QUITADO = 'QUITADO'
    STATUS_CANCELADO = 'CANCELADO'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_QUITADO, 'Quitado'),
        (STATUS_CANCELADO, 'Cancelado'),
    ]

    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.CASCADE,
        related_name='acordos',
        verbose_name='Unidade',
    )
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor Total',
    )
    numero_parcelas = models.PositiveIntegerField(verbose_name='Número de Parcelas')
    data_criacao = models.DateField(auto_now_add=True, verbose_name='Data de Criação')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVO,
        verbose_name='Status',
        db_index=True,
    )
    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'acordos'
        verbose_name = 'Acordo'
        verbose_name_plural = 'Acordos'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['unidade', 'status']),
        ]

    def __str__(self):
        return f'Acordo {self.id} - {self.unidade} ({self.status})'


class AcordoParcela(models.Model):

    STATUS_PENDENTE = 'PENDENTE'
    STATUS_PAGO = 'PAGO'
    STATUS_VENCIDO = 'VENCIDO'
    STATUS_CANCELADO = 'CANCELADO'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_PAGO, 'Pago'),
        (STATUS_VENCIDO, 'Vencido'),
        (STATUS_CANCELADO, 'Cancelado'),
    ]

    acordo = models.ForeignKey(
        Acordo,
        on_delete=models.CASCADE,
        related_name='parcelas',
        verbose_name='Acordo',
    )
    numero_parcela = models.PositiveIntegerField(verbose_name='Número da Parcela')
    valor_parcela = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor da Parcela',
    )
    data_vencimento = models.DateField(verbose_name='Data de Vencimento', db_index=True)
    data_pagamento = models.DateField(null=True, blank=True, verbose_name='Data de Pagamento')
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Multa')
    juros = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Juros')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
        verbose_name='Status',
        db_index=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'acordo_parcelas'
        verbose_name = 'Parcela do Acordo'
        verbose_name_plural = 'Parcelas do Acordo'
        ordering = ['acordo', 'numero_parcela']
        constraints = [
            models.UniqueConstraint(
                fields=['acordo', 'numero_parcela'],
                name='unique_parcela_por_acordo'
            )
        ]

    def __str__(self):
        return f'Parcela {self.numero_parcela}/{self.acordo.numero_parcelas} - Acordo {self.acordo.id}'
