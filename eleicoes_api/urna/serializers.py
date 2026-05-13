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

class CandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidato
        fields = '__all__'

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

