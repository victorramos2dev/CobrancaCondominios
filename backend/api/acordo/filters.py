import django_filters
from .models import Acordo


class AcordoFilter(django_filters.FilterSet):
    unidade = django_filters.NumberFilter(field_name='unidade__id')
    condominio = django_filters.NumberFilter(field_name='unidade__condominio__id')
    status = django_filters.ChoiceFilter(choices=Acordo.STATUS_CHOICES)
    criado_de = django_filters.DateFilter(field_name='data_criacao', lookup_expr='gte')
    criado_ate = django_filters.DateFilter(field_name='data_criacao', lookup_expr='lte')

    class Meta:
        model = Acordo
        fields = ['unidade', 'condominio', 'status']
