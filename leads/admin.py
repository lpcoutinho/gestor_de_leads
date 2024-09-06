from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sexo', 'telefone', 'valor_hora', 'midias', 'idade', 'seguidores', 'local', 'cidade', 'estado', 'quem_atende', 'url')
