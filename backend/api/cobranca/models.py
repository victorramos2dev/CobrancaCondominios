from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from api.unidade.models import Unidade


class Cobranca(models.Model):

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

    FORMA_BOLETO = 'BOLETO'
    FORMA_PIX = 'PIX'
    FORMA_CARTAO = 'CARTAO'

    FORMA_CHOICES = [
        (FORMA_BOLETO, 'Boleto'),
        (FORMA_PIX, 'Pix'),
        (FORMA_CARTAO, 'Cartão'),
    ]

    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.CASCADE,
        related_name='cobrancas',
        verbose_name='Unidade',
    )
    competencia = models.DateField(verbose_name='Competência', db_index=True)
    data_vencimento = models.DateField(verbose_name='Data de Vencimento', db_index=True)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
        verbose_name='Status',
        db_index=True,
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Pagamento',
    )
    forma_pagamento = models.CharField(
        max_length=10,
        choices=FORMA_CHOICES,
        null=True,
        blank=True,
        verbose_name='Forma de Pagamento',
    )
    multa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Multa (R$)',
    )
    juros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Juros (R$)',
    )

    acordo = models.ForeignKey(
        'acordo.Acordo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cobrancas',
        verbose_name='Acordo',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cobrancas'
        verbose_name = 'Cobrança'
        verbose_name_plural = 'Cobranças'
        ordering = ['-data_vencimento']
        indexes = [
            models.Index(fields=['unidade', 'status']),
            models.Index(fields=['data_vencimento', 'status']),
            models.Index(fields=['competencia']),
        ]

    def __str__(self):
        return f'Cobrança {self.id} - {self.unidade} - {self.competencia}'

    def clean(self):
        if self.status == self.STATUS_PAGO and not self.data_pagamento:
            raise ValidationError({
            })

    @property
    def valor_total(self):
        return self.valor + self.multa + self.juros

    @property
    def dias_atraso(self):
        ref = self.data_pagamento or timezone.localdate()
        if ref > self.data_vencimento:
            return (ref - self.data_vencimento).days
        return 0
