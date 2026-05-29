from rest_framework import serializers
from .models import Unidade
from api.condominio.models import Condominio


class UnidadeSerializer(serializers.ModelSerializer):
    condominio_nome = serializers.CharField(source='condominio.nome', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome', read_only=True)

    class Meta:
        model = Unidade
        fields = [
            'id', 'numero', 'bloco', 'status',
            'condominio', 'condominio_nome',
            'responsavel', 'responsavel_nome',
            'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def validate(self, attrs):
        condominio = attrs.get('condominio', getattr(self.instance, 'condominio', None))
        bloco = attrs.get('bloco', getattr(self.instance, 'bloco', None))
        numero = attrs.get('numero', getattr(self.instance, 'numero', None))

        qs = Unidade.objects.filter(condominio=condominio, bloco=bloco, numero=numero)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Já existe uma unidade com este número/bloco neste condomínio.'
            )
        return attrs
