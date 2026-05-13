from django.db import models
from django.core.exceptions import ValidationError


class Eleitor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class TipoChoices(models.TextChoices):
    ESTUDANTIL = 'ESTUDANTIL', 'Estudantil'
    SINDICAL = 'SINDICAL', 'Sindical'
    ASSOCIACAO = 'ASSOCIACAO', 'Associação'
    CONDOMINIO = 'CONDOMINIO', 'Condomínio'
    CONSELHO = 'CONSELHO', 'Conselho'
    OUTRA = 'OUTRA', 'Outra'

class StatusChoices(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    ABERTA = 'ABERTA', 'Aberta'
    ENCERRADA = 'ENCERRADA', 'Encerrada'
    APURADA = 'APURADA', 'Apurada'
  
class Eleicao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=50, choices=TipoChoices.choices)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.RASCUNHO)
    permite_branco = models.BooleanField(default=False)
    criada_por = models.ForeignKey(Eleitor, on_delete=models.CASCADE, related_name='eleicoes_criadas')

    def clean(self):
        super().clean()

        if self.data_inicio and self.data_fim:  
            if self.data_fim <= self.data_inicio:
                raise ValidationError({
                    'data_fim': 'A data de fim deve ser maior que a data de início.'
                })

        if self.pk:
            eleicao_anterior = Eleicao.objects.get(pk=self.pk)

            fluxo = {
                StatusChoices.RASCUNHO: StatusChoices.ABERTA,
                StatusChoices.ABERTA: StatusChoices.ENCERRADA,
                StatusChoices.ENCERRADA: StatusChoices.APURADA,
            }

            status_atual = eleicao_anterior.status
            novo_status = self.status

            if status_atual != novo_status:
                proximo_status = fluxo.get(status_atual)

                if novo_status != proximo_status:
                    raise ValidationError({
                        'status': (
                            'O status só pode seguir o fluxo: '
                            'rascunho -> aberta -> encerrada -> apurada.'
                        )
                    })

    def __str__(self):
        return self.titulo
    
class Candidato (models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='candidatos')
    numero = models.PositiveIntegerField()
    nome = models.CharField(max_length=150)
    nome_urna = models.CharField(max_length=50)
    partido_ou_chapa = models.CharField(max_length=100, blank=True)
    proposta = models.TextField(blank=True)
    foto_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.nome} ({self.numero})"

class AptidaoEleitor(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='aptidoes')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='aptos')
    data_inclusao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('eleitor', 'eleicao')]

    def __str__(self):
        return f"{self.eleitor} – {self.eleicao}"

class RegistroVotacao(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='registros_votacao')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='registros_votacao')
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('eleitor', 'eleicao')]

    def __str__(self):
        return f"{self.eleitor} votou em {self.eleicao} em {self.data_hora}"

class Voto(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='votos')
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='votos', null=True, blank=True)
    em_branco = models.BooleanField(default=False)
    data_hora = models.DateTimeField(auto_now_add=True)
    comprovante_hash = models.CharField(max_length=64, unique=True)

    def clean(self):
        super().clean()

        valido = (
            (self.em_branco is True and self.candidato is None) or
            (self.em_branco is False and self.candidato is not None)
        )

        if not valido:
            raise ValidationError(
                "O voto deve ser em branco sem candidato OU " "não ser em branco com um candidato definido."
            )