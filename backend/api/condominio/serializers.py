from rest_framework import serializers
from .models import Condominio, ConfiguracaoMulta


class CondominioSerializer(serializers.ModelSerializer):
    total_unidades = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Condominio
        fields = [
            'id', 'nome', 'cnpj', 'endereco', 'status',
            'total_unidades', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def get_total_unidades(self, obj):
        return obj.unidades.count()

    def validate_nome(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('O nome deve ter pelo menos 3 caracteres.')
        return value.strip()

