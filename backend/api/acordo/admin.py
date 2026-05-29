from django.contrib import admin
from .models import Acordo, AcordoParcela

@admin.register(Acordo)
class AcordoAdmin(admin.ModelAdmin):
    list_display = ['id', 'unidade', 'valor_total', 'numero_parcelas', 'status', 'data_criacao']
    list_filter = ['status']

@admin.register(AcordoParcela)
class AcordoParcelaAdmin(admin.ModelAdmin):
    list_display = ['id', 'acordo', 'numero_parcela', 'valor_parcela', 'data_vencimento', 'status']
    list_filter = ['status']
