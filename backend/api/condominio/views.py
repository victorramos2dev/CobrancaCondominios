from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from condominios.permissions import IsAdminOrReadOnly
from condominios.paginations import CondominiosPagination
from .models import Condominio, ConfiguracaoMulta
from .serializers import CondominioSerializer
from .serializers_multa import ConfiguracaoMultaSerializer


class CondominioViewSet(viewsets.ModelViewSet):
    queryset = Condominio.objects.all().order_by('nome')
    serializer_class = CondominioSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CondominiosPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['nome', 'cnpj']
    ordering_fields = ['nome', 'criado_em']

class ConfiguracaoMultaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracaoMulta.objects.select_related('condominio').all()
    serializer_class = ConfiguracaoMultaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['condominio','ativo']


