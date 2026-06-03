from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction
from api.acordo.models import Acordo, AcordoParcela
from api.cobranca.models import Cobranca
from api.cobranca.services import calcular_multa_juros
from django.utils import timezone


@transaction.atomic
def criar_acordo(unidade, cobranca_ids: list, numero_parcelas: int, observacao: str = '') -> Acordo:
    if numero_parcelas < 1:
        raise ValueError('O número de parcelas deve ser pelo menos 1.')

    cobrancas = Cobranca.objects.filter(id__in=cobranca_ids)

    if cobrancas.count() != len(cobranca_ids):
        raise ValueError('Uma ou mais cobranças não foram encontradas.')

    unidades_ids = set(cobrancas.values_list('unidade_id', flat=True))
    if len(unidades_ids) > 1:
        raise ValueError('Todas as cobranças devem pertencer à mesma unidade.')
    if unidade.id not in unidades_ids:
        raise ValueError('As cobranças não pertencem à unidade informada.')

    nao_vencidas = cobrancas.exclude(status=Cobranca.STATUS_VENCIDO)
    if nao_vencidas.exists():
        nomes = list(nao_vencidas.values_list('id', flat=True))
        raise ValueError(f'Cobranças {nomes} não estão com status VENCIDO.')

    valor_total = sum(
        c.valor + c.multa + c.juros for c in cobrancas
    )

    acordo = Acordo.objects.create(
        unidade=unidade,
        valor_total=valor_total,
        numero_parcelas=numero_parcelas,
        observacao=observacao,
    )

    cobrancas.update(acordo=acordo)

    _gerar_parcelas(acordo, valor_total, numero_parcelas)

    return acordo


def _gerar_parcelas(acordo: Acordo, valor_total: Decimal, numero_parcelas: int):
    valor_parcela = (valor_total / numero_parcelas).quantize(Decimal('0.01'))
    total_calculado = valor_parcela * numero_parcelas
    diferenca = valor_total - total_calculado

    parcelas = []
    hoje = date.today()
    for i in range(1, numero_parcelas + 1):
        venc = hoje + relativedelta(months=i)
        val = valor_parcela + (diferenca if i == numero_parcelas else Decimal('0'))
        parcelas.append(AcordoParcela(
            acordo=acordo,
            numero_parcela=i,
            valor_parcela=val,
            data_vencimento=venc,
        ))

    AcordoParcela.objects.bulk_create(parcelas)

@transaction.atomic
def registrar_pagamento_parcela(parcela: AcordoParcela, data_pagamento, usuario=None) -> AcordoParcela:
    if parcela.status == AcordoParcela.STATUS_PAGO:
        raise ValueError('Essa parcela já está paga.')
    if parcela.status == AcordoParcela.STATUS_CANCELADO:
        raise ValueError('Não é possivel pagar uma parcela cancelada')
    
    calc = calcular_multa_juros(
        valor=parcela.valor_parcela,
        data_vencimento=parcela.data_vencimento,
        data_pagamento=data_pagamento,
        unidade=parcela.acordo.unidade,
    )
    
    parcela.data_pagamento = data_pagamento
    parcela.multa = calc['multa']
    parcela.juros = calc['juros']
    parcela.status = AcordoParcela.STATUS_PAGO
    parcela.save()
    
    todas_pagas = not parcela.acordo.parcelas.exclude(
        status=AcordoParcela.STATUS_PAGO
    ).exists()
    
    if todas_pagas:
        parcela.acordo.status = Acordo.STATUS_QUITADO
        parcela.acordo.save(update_fields=['status','atualizado_em'])
    
    return parcela
