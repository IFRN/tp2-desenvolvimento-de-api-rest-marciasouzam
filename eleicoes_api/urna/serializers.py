from rest_framework import serializers

from .models import (Eleitor, Eleicao, Candidato, AptidaoEleitor, RegistroVotacao, Voto, StatusChoices, TipoChoices)
  

class EleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = '__all__'

class EleicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleicao
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_total_candidatos(self, obj):
        return obj.candidatos.count()

    def get_total_aptos(self, obj):
        return obj.aptos.count()

class CandidatoSerializer(serializers.ModelSerializer):
    eleicao_titulo = serializers.CharField(source='eleicao.titulo', read_only=True)
    class Meta:
        model = Candidato
        fields = '__all__'

        def validate_numero(self, value):
            if value == 0:
                raise serializers.ValidationError(
                    "O número 0 é reservado para voto em branco e não pode ser atribuído a um candidato."
                )
            return value

class AptidaoEleitorSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleitor.nome', read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo', read_only=True)
    class Meta:
        model = AptidaoEleitor
        fields = '__all__'

class RegistroVotacaoSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleitor.nome', read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo', read_only=True)
    class Meta:
        model = RegistroVotacao
        fields = '__all__'

class VotoSerializer(serializers.ModelSerializer):
    candidato_nome_urna = serializers.CharField(source='candidato.nome_urna', read_only=True, allow_null=True)
    em_branco_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Voto
        fields = '__all__'

    def get_em_branco_display(self, obj):
        return 'BRANCO' if obj.em_branco else None
    
class VotacaoInputSerializer(serializers.Serializer):
    eleitor_id   = serializers.IntegerField()
    eleicao_id   = serializers.IntegerField()
    candidato_id = serializers.IntegerField(required=False, allow_null=True)
    em_branco    = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        try:
            eleicao = Eleicao.objects.get(pk=data['eleicao_id'])
        except Eleicao.DoesNotExist:
            raise serializers.ValidationError("Eleição não encontrada.")

        if eleicao.status != StatusChoices.ABERTA:
            raise serializers.ValidationError("A eleição não está aberta.")
    
    


