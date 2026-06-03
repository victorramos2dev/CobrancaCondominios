from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from condominios.permissions import IsAdminOrReadOnly
from condominios.paginations import CondominiosPagination
from .models import Cobranca
from .serializers import CobrancaSerializer, CobrancaPagamentoSerializer
from .filters import CobrancaFilter
from .services import registrar_pagamento, atualizar_status_vencidas


class CobrancaViewSet(viewsets.ModelViewSet):
    queryset = Cobranca.objects.select_related(
        'unidade', 'unidade__condominio'
    ).order_by('-data_vencimento')
    serializer_class = CobrancaSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CobrancaFilter
    search_fields = ['unidade__numero', 'unidade__condominio__nome']
    ordering_fields = ['data_vencimento', 'valor', 'competencia', 'status']

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            atualizar_status_vencidas()
        return super().get_queryset()

    @action(detail=True, methods=['post'], url_path='pagar')
    def pagar(self, request, pk=None):
        """
        POST /api/cobrancas/{id}/pagar/
        Registra pagamento com cálculo automático de multa e juros.
        """
        cobranca = self.get_object()
        serializer = CobrancaPagamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cobranca = registrar_pagamento(
                cobranca,
                serializer.validated_data['data_pagamento'],
                serializer.validated_data['forma_pagamento'],
                usuario=request.user,
            )
        except ValueError as e:
            return Response(
                {'success': False, 'message': str(e), 'errors': {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(CobrancaSerializer(cobranca).data)

    @action(detail=False, methods=['post'], url_path='atualizar-vencidas')
    def atualizar_vencidas(self, request):
        """
        POST /api/cobrancas/atualizar-vencidas/
        Marca cobranças pendentes com vencimento passado como VENCIDAS.
        """
        total = atualizar_status_vencidas()
        return Response({
            'success': True,
            'message': f'{total} cobrança(s) marcada(s) como VENCIDA(S).',
            'total_atualizado': total,
        })
