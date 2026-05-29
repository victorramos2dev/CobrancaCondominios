from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from django_filters.rest_framework import DjangoFilterBackend
from condominios.permissions import IsAdminOrReadOnly
from condominios.paginations import CondominiosPagination
from .models import Acordo, AcordoParcela
from .serializers import AcordoSerializer, AcordoParcelaSerializer
from .filters import AcordoFilter
from .services import registrar_pagamento_parcela

class AcordoViewSet(viewsets.ModelViewSet):
    queryset = Acordo.objects.select_related(
        'unidade', 'unidade__condominio'
    ).prefetch_related('parcelas').order_by('-criado_em')
    serializer_class = AcordoSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AcordoFilter
    search_fields = ['unidade__numero', 'unidade__condominio__nome']
    ordering_fields = ['data_criacao', 'valor_total']


class AcordoParcelaViewSet(viewsets.ModelViewSet):
    queryset = AcordoParcela.objects.select_related('acordo').order_by('acordo', 'numero_parcela')
    serializer_class = AcordoParcelaSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['acordo', 'status']
    ordering_fields = ['data_vencimento', 'numero_parcela']
    
    @action(detail=True, methods=['post'], url_path='pagar')
    def pagar(self, request, pk=None):
        parcela = self.get_object()
        serializer = PagamentoParcelaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            parcela = registrar_pagamento_parcela(
                parcela,
                serializer.validated_data['data_pagamento'],
                usuario=request.user,
            )
        except ValueError as e:
            return Response(
                {'sucess': False, 'message':str(e), 'errors':{}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(AcordoParcelaSerializer(parcela).data)

class PagamentoParcelaSerializer(drf_serializers.Serializer):
    data_pagamento = drf_serializers.DateField(required=True)

