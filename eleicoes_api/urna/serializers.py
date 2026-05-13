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
        
        agora = timezone.now()
        if not (eleicao.data_inicio <= agora <= eleicao.data_fim):
            raise serializers.ValidationError("A eleição ainda não começou.")
        
        try:
            eleitor = Eleitor.objects.get(pk=data['eleitor_id'])
        except Eleitor.DoesNotExist:
            raise serializers.ValidationError("Eleitor não encontrado.")
        
        if not eleicao.aptos.filter(pk=eleitor.pk).exists():
            raise serializers.ValidationError("Eleitor não apto para votar nesta eleição.")
        
        if RegistroVotacao.objects.filter(eleitor=eleitor, eleicao=eleicao).exists():
            raise serializers.ValidationError("Eleitor já votou nesta eleição.")
        
        candidato_id = data.get('candidato_id')
        if candidato_id:
            try: 
                candidato = Candidato.objects.get(pk=candidato_id, eleicao=eleicao)
            except Candidato.DoesNotExist:
                raise serializers.ValidationError("Candidato não encontrado para esta eleição.")
            
            if candidato.eleicao_id != eleicao.pk:
                raise serializers.ValidationError("Candidato não pertence a esta eleição.")
            data ['candidato'] = candidato

            tem_candidato = bool(candidato_id)
            em_branco = data.get('em_branco', False)

            if tem_candidato and em_branco:
                raise serializers.ValidationError("Não é possível votar em um candidato e em branco ao mesmo tempo.")
            if not tem_candidato and not em_branco:
                raise serializers.ValidationError("É necessário votar em um candidato ou em branco.")
            
            data['eleicao'] = eleicao
            data['eleitor'] = eleitor
            return data
        
    


