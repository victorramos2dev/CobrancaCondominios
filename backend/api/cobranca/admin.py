from django.contrib import admin
from .models import Cobranca

@admin.register(Cobranca)
class CobrancaAdmin(admin.ModelAdmin):
    list_display = ['id', 'unidade', 'competencia', 'data_vencimento', 'valor', 'status', 'multa', 'juros']
    list_filter = ['status', 'forma_pagamento']
    search_fields = ['unidade__numero']
    date_hierarchy = 'data_vencimento'
