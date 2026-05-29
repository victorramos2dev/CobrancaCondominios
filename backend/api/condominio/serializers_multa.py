from rest_framework import serializers
from .models import ConfiguracaoMulta

class ConfiguracaoMultaSerializer(serializers.ModelSerializer):
    condominio_nome = serializers.CharField(source='condominio.nome', read_only=True)
    
    class Meta:
        model = ConfiguracaoMulta
        fields = [
            'id', 'condominio', 'condominio_nome','percentual_multa',
            'percentual_juros_dia','ativo','atualizado_em',
        ]
        read_only_fields = ['atualizado_em']