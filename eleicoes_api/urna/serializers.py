from rest_framework import serializers

from .models import (Eleitor, Eleicao, Candidato, AptidaoEleitor, RegistroVotacao, Voto)

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
    class Meta:
        model = AptidaoEleitor
        fields = '__all__'

class RegistroVotacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroVotacao
        fields = '__all__'

class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voto
        fields = '__all__'

