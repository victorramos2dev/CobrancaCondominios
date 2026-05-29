from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from condominios.permissions import IsAdminOrReadOnly
from condominios.paginations import CondominiosPagination
from .models import Unidade
from .serializers import UnidadeSerializer
from api.cobranca.models import Cobranca
from api.acordo.models import Acordo


class UnidadeViewSet(viewsets.ModelViewSet):
    queryset = Unidade.objects.select_related('condominio', 'responsavel').order_by('id')
    serializer_class = UnidadeSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['condominio', 'status']
    search_fields = ['numero', 'bloco', 'responsavel__nome']
    ordering_fields = ['numero', 'bloco', 'criado_em']

    @action(detail=True, methods=['get'], url_path='resumo-financeiro')
    def resumo_financeiro(self, request, pk=None):
        """
        GET /api/unidades/{id}/resumo-financeiro/
        Retorna resumo financeiro da unidade.
        """
        try:
            unidade = Unidade.objects.select_related('responsavel').get(pk=pk)
        except Unidade.DoesNotExist:
            raise NotFound('Unidade não encontrada.')

        cobrancas = Cobranca.objects.filter(unidade=unidade)
        total = cobrancas.count()
        pagas = cobrancas.filter(status=Cobranca.STATUS_PAGO).count()
        vencidas = cobrancas.filter(status=Cobranca.STATUS_VENCIDO).count()
        pendentes = cobrancas.filter(status=Cobranca.STATUS_PENDENTE).count()

        valor_em_aberto = cobrancas.filter(
            status__in=[Cobranca.STATUS_VENCIDO, Cobranca.STATUS_PENDENTE]
        ).aggregate(total=Sum('valor'))['total'] or 0

        possui_acordo = Acordo.objects.filter(
            unidade=unidade,
            status=Acordo.STATUS_ATIVO
        ).exists()

        return Response({
            'unidade': unidade.id,
            'numero': unidade.numero,
            'bloco': unidade.bloco,
            'responsavel': unidade.responsavel.nome if unidade.responsavel else None,
            'total_cobrancas': total,
            'total_pagas': pagas,
            'total_vencidas': vencidas,
            'total_pendentes': pendentes,
            'valor_em_aberto': float(valor_em_aberto),
            'possui_acordo': possui_acordo,
        })
