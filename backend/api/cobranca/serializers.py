from rest_framework import serializers
from django.utils import timezone
from .models import Cobranca
from api.cobranca.services import calcular_multa_juros


class CobrancaSerializer(serializers.ModelSerializer):
    unidade_numero = serializers.CharField(source='unidade.numero', read_only=True)
    condominio_nome = serializers.CharField(source='unidade.condominio.nome', read_only=True)
    condominio_id = serializers.IntegerField(source='unidade.condominio.id', read_only=True)
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cobranca
        fields = [
            'id', 'unidade', 'unidade_numero', 'condominio_id', 'condominio_nome',
            'competencia', 'data_vencimento', 'valor', 'status',
            'data_pagamento', 'forma_pagamento',
            'multa', 'juros', 'valor_total', 'dias_atraso',
            'acordo', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['multa', 'juros', 'criado_em', 'atualizado_em', 'acordo']

    def validate(self, attrs):
        status = attrs.get('status', getattr(self.instance, 'status', Cobranca.STATUS_PENDENTE))
        data_pagamento = attrs.get('data_pagamento', getattr(self.instance, 'data_pagamento', None))
        data_vencimento = attrs.get('data_vencimento', getattr(self.instance, 'data_vencimento', None))

        if status == Cobranca.STATUS_PAGO and not data_pagamento:
            raise serializers.ValidationError({
                'data_pagamento': 'Data de pagamento é obrigatória quando o status é PAGO.'
            })

        if status == Cobranca.STATUS_PAGO and data_pagamento and data_vencimento:
            valor = attrs.get('valor', getattr(self.instance, 'valor', None))
            if valor:
                unidade = attrs.get('unidade',getattr(self.instance, 'unidade', None))
                calc = calcular_multa_juros(valor, data_vencimento,data_pagamento, unidade=unidade)
                attrs['multa'] = calc['multa']
                attrs['juros'] = calc['juros']

        forma = attrs.get('forma_pagamento', None)
        if forma and status != Cobranca.STATUS_PAGO:
            raise serializers.ValidationError({
                'forma_pagamento': 'Forma de pagamento só pode ser informada quando status é PAGO.'
            })

        return attrs


class CobrancaPagamentoSerializer(serializers.Serializer):
    data_pagamento = serializers.DateField(required=True)
    forma_pagamento = serializers.ChoiceField(choices=Cobranca.FORMA_CHOICES, required=True)
