from django.db import models
from api.condominio.models import Condominio
from api.usuarios.models import Usuario


class Unidade(models.Model):

    STATUS_OCUPADO = 'OCUPADO'
    STATUS_VAGO = 'VAGO'

    STATUS_CHOICES = [
        (STATUS_OCUPADO, 'Ocupado'),
        (STATUS_VAGO, 'Vago'),
    ]

    numero = models.CharField(max_length=10, verbose_name='Número')
    bloco = models.CharField(max_length=10, blank=True, null=True, verbose_name='Bloco')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_VAGO,
        verbose_name='Status',
        db_index=True,
    )
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='unidades',
        verbose_name='Condomínio',
    )
    responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidades',
        verbose_name='Responsável',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unidades'
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        ordering = ['condominio', 'bloco', 'numero']
        indexes = [
            models.Index(fields=['condominio', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'bloco', 'numero'],
                name='unique_unidade_por_condominio'
            )
        ]

    def __str__(self):
        bloco = f'Bloco {self.bloco} ' if self.bloco else ''
        return f'{bloco}Unidade {self.numero} - {self.condominio.nome}'
