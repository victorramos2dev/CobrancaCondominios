from django.contrib import admin
from .models import Unidade

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'numero', 'bloco', 'condominio', 'responsavel', 'status']
    list_filter = ['status', 'condominio']
    search_fields = ['numero', 'bloco']
