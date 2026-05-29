from rest_framework import serializers
from .models import Acordo, AcordoParcela
from api.cobranca.models import Cobranca


class AcordoParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcordoParcela
        fields = [
            'id', 'acordo', 'numero_parcela', 'valor_parcela',
            'data_vencimento', 'data_pagamento',
            'multa', 'juros', 'status', 'criado_em',
        ]
        read_only_fields = ['criado_em']


class AcordoSerializer(serializers.ModelSerializer):
    parcelas = AcordoParcelaSerializer(many=True, read_only=True)
    unidade_numero = serializers.CharField(source='unidade.numero', read_only=True)
    condominio_nome = serializers.CharField(source='unidade.condominio.nome', read_only=True)
    cobrancas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text='Lista de IDs de cobranças VENCIDAS da mesma unidade.',
    )

    class Meta:
        model = Acordo
        fields = [
            'id', 'unidade', 'unidade_numero', 'condominio_nome',
            'valor_total', 'numero_parcelas', 'data_criacao',
            'status', 'observacao',
            'cobrancas_ids',
            'parcelas',
            'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['valor_total', 'data_criacao', 'criado_em', 'atualizado_em']

    def validate_numero_parcelas(self, value):
        if value < 1:
            raise serializers.ValidationError('O número de parcelas deve ser pelo menos 1.')
        if value > 60:
            raise serializers.ValidationError('O número de parcelas não pode exceder 60.')
        return value

    def validate(self, attrs):
        cobranca_ids = attrs.get('cobrancas_ids', [])
        if not cobranca_ids:
            raise serializers.ValidationError({'cobrancas_ids': 'Informe ao menos uma cobrança.'})
        return attrs

    def create(self, validated_data):
        from api.acordo.services import criar_acordo
        cobranca_ids = validated_data.pop('cobrancas_ids')
        unidade = validated_data['unidade']
        numero_parcelas = validated_data['numero_parcelas']
        observacao = validated_data.get('observacao', '')
        try:
            return criar_acordo(unidade, cobranca_ids, numero_parcelas, observacao)
        except ValueError as e:
            raise serializers.ValidationError({'detail': str(e)})
