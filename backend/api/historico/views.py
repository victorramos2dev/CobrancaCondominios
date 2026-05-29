from rest_framework import viewsets, serializers, filters
from django_filters.rest_framework import DjangoFilterBackend
from condominios.permissions import IsAdminOrReadOnly
from condominios.paginations import CondominiosPagination
from .models import HistoricoStatus


class HistoricoStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoStatus
        fields = ['id', 'cobranca', 'status_anterior', 'status_novo', 'data_alteracao', 'usuario']
        read_only_fields = fields


class HistoricoStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistoricoStatus.objects.select_related('cobranca').order_by('-data_alteracao')
    serializer_class = HistoricoStatusSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['cobranca']
    ordering_fields = ['data_alteracao']
