from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CondominiosPagination(PageNumberPagination):
    """
    Paginação padrão do projeto.

    Query params:
        page       – número da página (padrão: 1)
        page_size  – itens por página (padrão: 50, máx: 200)
        all        – se "true", desativa paginação e retorna tudo (use com cuidado)
    """
    page_size              = 50
    page_size_query_param  = 'page_size'
    max_page_size          = 200
    page_query_param       = 'page'

    def paginate_queryset(self, queryset, request, view=None):
        # ?all=true → desabilita paginação para este request
        if request.query_params.get('all', '').lower() == 'true':
            return None          # DRF trata None como "não paginado"
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'count':    self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page':     self.page.number,
            'next':     self.get_next_link(),
            'previous': self.get_previous_link(),
            'results':  data,
        })

    def get_paginated_response_schema(self, schema):   # para drf-spectacular
        return {
            'type': 'object',
            'properties': {
                'count':       {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'page':        {'type': 'integer'},
                'next':        {'type': 'string', 'nullable': True},
                'previous':    {'type': 'string', 'nullable': True},
                'results':     schema,
            },
        }
