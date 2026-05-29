from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from api.cobranca.models import Cobranca
from api.historico.models import HistoricoStatus

def _get_taxas(unidade) -> dict:
    
    from api.condominio.models import ConfiguracaoMulta
    
    try:
        config = ConfiguracaoMulta.objects.get(
            condominio=unidade.condominio,
            ativo=True
        )
        return{
            'multa': config.percentual_multa,
            'juros_dia': config.percentual_juros_dia,
        }
    except ConfiguracaoMulta.DoesNotExist:
        return{
            'multa': Decimal('0.02'),
            'juros_dia': Decimal('0.00033'),
        }

def calcular_multa_juros(valor: Decimal, data_vencimento, data_pagamento, unidade = None) -> dict:

    multa = Decimal('0')
    juros = Decimal('0')

    if data_pagamento and data_pagamento > data_vencimento:
        taxas = _get_taxas(unidade) if unidade else {
            'multa': Decimal('0.02'),
            'juros_dia': Decimal('0.00033'),
        }
        dias = (data_pagamento - data_vencimento).days
        multa = (valor * taxas['multa']).quantize(Decimal('0.01'))
        juros = (valor * taxas['juros_dia'] * dias).quantize(Decimal('0.01'))

    return {
        'multa': multa,
        'juros': juros,
        'valor_total': valor + multa + juros,
        'dias_atraso': max(0, (data_pagamento - data_vencimento).days) if data_pagamento else 0,
    }


def atualizar_status_vencidas():
    """
    Marca como VENCIDO todas as cobranças com data_vencimento < hoje
    e status PENDENTE. Retorna quantidade atualizada.
    """
    hoje = timezone.localdate()
    cobrancas = Cobranca.objects.filter(
        data_vencimento__lt=hoje,
        status=Cobranca.STATUS_PENDENTE,
    )
    total = 0
    for c in cobrancas:
        _registrar_historico(c, Cobranca.STATUS_PENDENTE, Cobranca.STATUS_VENCIDO)
        c.status = Cobranca.STATUS_VENCIDO
        c.save(update_fields=['status', 'atualizado_em'])
        total += 1
    return total


@transaction.atomic
def registrar_pagamento(cobranca: Cobranca, data_pagamento, forma_pagamento: str, usuario=None) -> Cobranca:
    """
    Registra pagamento de uma cobrança:
    - Calcula multa e juros se após vencimento
    - Muda status para PAGO
    - Grava histórico
    """
    if cobranca.status == Cobranca.STATUS_PAGO:
        raise ValueError('Esta cobrança já está paga.')
    if cobranca.status == Cobranca.STATUS_CANCELADO:
        raise ValueError('Não é possível pagar uma cobrança cancelada.')

    calc = calcular_multa_juros(cobranca.valor, cobranca.data_vencimento, data_pagamento, unidade=cobranca.unidade)

    status_anterior = cobranca.status
    cobranca.data_pagamento = data_pagamento
    cobranca.forma_pagamento = forma_pagamento
    cobranca.multa = calc['multa']
    cobranca.juros = calc['juros']
    cobranca.status = Cobranca.STATUS_PAGO
    cobranca.save()

    _registrar_historico(cobranca, status_anterior, Cobranca.STATUS_PAGO, usuario)
    return cobranca


def _registrar_historico(cobranca: Cobranca, status_anterior: str, status_novo: str, usuario=None):
    HistoricoStatus.objects.create(
        cobranca=cobranca,
        status_anterior=status_anterior,
        status_novo=status_novo,
        usuario=str(usuario) if usuario else None,
    )
