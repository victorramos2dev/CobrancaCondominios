from django.contrib import admin
from .models import HistoricoStatus

@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'cobranca', 'status_anterior', 'status_novo', 'data_alteracao', 'usuario']
    list_filter = ['status_novo']
