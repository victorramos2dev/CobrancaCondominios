import django_filters
from .models import Cobranca


class CobrancaFilter(django_filters.FilterSet):
    unidade = django_filters.NumberFilter(field_name='unidade__id')
    condominio = django_filters.NumberFilter(field_name='unidade__condominio__id')
    status = django_filters.ChoiceFilter(choices=Cobranca.STATUS_CHOICES)
    competencia = django_filters.DateFilter(field_name='competencia')
    competencia_mes = django_filters.NumberFilter(field_name='competencia__month')
    competencia_ano = django_filters.NumberFilter(field_name='competencia__year')
    vencimento_de = django_filters.DateFilter(field_name='data_vencimento', lookup_expr='gte')
    vencimento_ate = django_filters.DateFilter(field_name='data_vencimento', lookup_expr='lte')

    class Meta:
        model = Cobranca
        fields = ['unidade', 'condominio', 'status', 'competencia']
