from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from api.condominio.models import Condominio
from api.unidade.models import Unidade
from api.cobranca.models import Cobranca
from api.cobranca.services import atualizar_status_vencidas
from api.acordo.models import Acordo


class DashboardView(APIView):
    """
    GET /api/dashboard/
    Retorna resumo financeiro geral do sistema.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        atualizar_status_vencidas()
        cobrancas = Cobranca.objects.all()

        total_pagas = cobrancas.filter(status=Cobranca.STATUS_PAGO)
        total_vencidas = cobrancas.filter(status=Cobranca.STATUS_VENCIDO)
        total_pendentes = cobrancas.filter(status=Cobranca.STATUS_PENDENTE)

        valor_recebido = total_pagas.aggregate(
            total=Sum('valor')
        )['total'] or 0

        valor_multa_juros = total_pagas.aggregate(
            multa=Sum('multa'), juros=Sum('juros')
        )
        valor_recebido_total = (
            float(valor_recebido)
            + float(valor_multa_juros['multa'] or 0)
            + float(valor_multa_juros['juros'] or 0)
        )

        valor_aberto = cobrancas.filter(
            status__in=[Cobranca.STATUS_VENCIDO, Cobranca.STATUS_PENDENTE]
        ).aggregate(total=Sum('valor'))['total'] or 0

        return Response({
            'total_condominios': Condominio.objects.filter(status=True).count(),
            'total_unidades': Unidade.objects.count(),
            'total_cobrancas': cobrancas.count(),
            'total_pagas': total_pagas.count(),
            'total_pendentes': total_pendentes.count(),
            'total_vencidas': total_vencidas.count(),
            'valor_total_recebido': round(valor_recebido_total, 2),
            'valor_total_em_aberto': round(float(valor_aberto), 2),
            'total_acordos': Acordo.objects.count(),
        })


class InadimplenciaResumoView(APIView):
    """
    GET /api/inadimplencia/resumo/
    Retorna resumo de inadimplência agrupado por condomínio.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        atualizar_status_vencidas()
        condominios = Condominio.objects.filter(status=True).prefetch_related('unidades')
        resultado = []

        for cond in condominios:
            vencidas = Cobranca.objects.filter(
                unidade__condominio=cond,
                status=Cobranca.STATUS_VENCIDO,
            )
            qtd = vencidas.count()
            if qtd == 0:
                continue
            valor = vencidas.aggregate(total=Sum('valor'))['total'] or 0
            resultado.append({
                'condominio_id': cond.id,
                'condominio': cond.nome,
                'qtd_cobrancas_vencidas': qtd,
                'valor_total_vencido': round(float(valor), 2),
            })

        resultado.sort(key=lambda x: x['valor_total_vencido'], reverse=True)
        return Response(resultado)
