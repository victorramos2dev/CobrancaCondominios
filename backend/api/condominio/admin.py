from django.contrib import admin
from .models import Condominio, ConfiguracaoMulta

@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'cnpj', 'endereco', 'status']
    list_filter = ['status']
    search_fields = ['nome', 'cnpj']
    

@admin.register(ConfiguracaoMulta)
class ConfiguracaoMultaAdmin(admin.ModelAdmin):
    list_display = ['condominio','percentual_multa','percentual_juros_dia','ativo','atualizado_em']
    list_filter = ['ativo']