from django.db import models

class Lead(models.Model):
    nome = models.CharField(max_length=255)
    sexo = models.CharField(max_length=20)
    telefone = models.CharField(max_length=20)
    valor_hora = models.FloatField()
    midias = models.CharField(max_length=255)
    idade = models.IntegerField()
    seguidores = models.IntegerField()
    local = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=2)
    quem_atende = models.CharField(max_length=255)
    url = models.URLField()
    status_lead = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.nome
