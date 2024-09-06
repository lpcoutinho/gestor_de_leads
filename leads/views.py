from django.shortcuts import render, get_object_or_404
from .models import Lead
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import send_message, update_lead_status
from django.core.paginator import Paginator
from django_filters import FilterSet, CharFilter, NumberFilter
import json
from time import sleep
import random
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

API_KEY = os.getenv('API_KEY')

# Lista de estados (ou você pode buscar isso de um banco de dados)
ESTADOS_BRASIL = [
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins')
]

LOCAL = [
    ('Sem local', 'Sem local'),
    ('Com local', 'Com local'),    
]

class LeadFilter(FilterSet):
    valor_hora = NumberFilter(field_name='valor_hora', lookup_expr='lte')  # Filtra valor hora <= valor fornecido
    midias = CharFilter(field_name='midias', lookup_expr='lte')  # Filtra mídias que contenham o valor fornecido
    idade = NumberFilter(field_name='idade', lookup_expr='lte')  # Filtra idade <= valor fornecido
    seguidores = NumberFilter(field_name='seguidores', lookup_expr='lte')  # Filtra seguidores <= valor fornecido
    local = CharFilter(lookup_expr='icontains')
    estado = CharFilter(lookup_expr='exact')
    quem_atende = CharFilter(lookup_expr='icontains')
    status_lead = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Lead
        fields = ['valor_hora', 'midias', 'idade', 'seguidores', 'local', 'estado', 'quem_atende', 'status_lead']


def lead_list(request):
    queryset = Lead.objects.all()
    
    # Aplicar o filtro de estado, se fornecido
    estado_selecionado = request.GET.get('estado', '')
    if estado_selecionado:
        queryset = queryset.filter(estado=estado_selecionado)

    # Aplicar o filtro de local, se fornecido
    local_selecionado = request.GET.get('local', '')
    if local_selecionado:
        queryset = queryset.filter(local=local_selecionado)

    # Aplicar o filtro de idade (<=), se fornecido
    idade_selecionada = request.GET.get('idade', '')
    if idade_selecionada.isdigit():
        queryset = queryset.filter(idade__lte=int(idade_selecionada))

    # Aplicar o filtro de valor hora (<=), se fornecido
    valor_hora_selecionado = request.GET.get('valor_hora', '')
    if valor_hora_selecionado.isdigit():
        queryset = queryset.filter(valor_hora__lte=int(valor_hora_selecionado))

    # Aplicar o filtro de mídias (icontains), se fornecido
    midias_selecionado = request.GET.get('midias', '')
    if midias_selecionado.isdigit():
        queryset = queryset.filter(midias__lte=midias_selecionado)

    # Aplicar o filtro de seguidores (<=), se fornecido
    seguidores_selecionado = request.GET.get('seguidores', '')
    if seguidores_selecionado.isdigit():
        queryset = queryset.filter(seguidores__lte=int(seguidores_selecionado))

    # Filtros adicionais com django-filter
    filter = LeadFilter(request.GET, queryset=queryset)
    paginator = Paginator(filter.qs, 50)  # Exibe 50 leads por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter': filter,
        'estados': ESTADOS_BRASIL,  # Passa a lista de estados para o template
        'tem_local': LOCAL,  # Passa a lista de locais para o template
        'estado_selecionado': estado_selecionado,  # Preserva o estado selecionado no filtro
        'tem_local_selecionado': local_selecionado,  # Preserva o local selecionado no filtro
        'idade_selecionada': idade_selecionada,  # Preserva a idade selecionada no filtro
        'valor_hora_selecionado': valor_hora_selecionado,  # Preserva o valor hora selecionado
        'midias_selecionado': midias_selecionado,  # Preserva as mídias selecionadas
        'seguidores_selecionado': seguidores_selecionado  # Preserva os seguidores selecionados
    }
    
    return render(request, 'leads/lead_list.html', context)


def send_message_and_update_status(request, lead_id):
    print("Iniciando o processamento de envio de mensagem")
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=lead_id)

        # Dados para a requisição
        nome = lead.nome
        idade = lead.idade
        seguidores = lead.seguidores
        midias = lead.midias
        phone_number = lead.telefone
        
        print(f"Processando lead: {nome}, telefone: {phone_number}")

        text_message = f"Oi, {nome}! Tudo bem? Vi que você tem {idade} anos, {seguidores} seguidores e {midias} fotos no fatalmodel."
        # API_KEY = 'LpTeste'  

        # Envia a mensagem
        try:
            response = send_message('5521964781930', text_message, API_KEY)  # Certifique-se de que phone_number está correto
            
            if 200 <= response.status_code < 300:
                # Atualiza o status do lead
                if update_lead_status(lead_id, 'Primeiro contato realizado'):
                    return JsonResponse({'status': 'Mensagem enviada e status atualizado com sucesso'})
                else:
                    return JsonResponse({'status': 'Mensagem enviada, mas falha ao atualizar status'}, status=500)
            else:
                return JsonResponse({'status': 'Erro ao enviar mensagem'}, status=response.status_code)
        except Exception as e:
            return JsonResponse({'status': 'Erro interno do servidor', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'Método não permitido'}, status=405)


def send_message_to_all(request):
    if request.method == 'POST':
        try:
            print("Iniciando o processamento de envio de mensagens")
            # Decodificar o corpo JSON da requisição
            body = json.loads(request.body)
            lead_ids = body.get('lead_ids', [])  # Lista de IDs de leads a serem notificados
            errors = []
            
            print(f"Leads recebidos: {lead_ids}")
            print(f"Número de leads: {len(lead_ids)}")
            
            # Usando enumerate para obter o índice e o lead_id
            for index, lead_id in enumerate(lead_ids):
                try:
                    lead = get_object_or_404(Lead, pk=lead_id)
                    nome = lead.nome
                    idade = lead.idade
                    seguidores = lead.seguidores
                    midias = lead.midias
                    phone_number = lead.telefone
                    print(f"Processando lead: {nome}, telefone: {phone_number}")
                    
                    # Enviar mensagem
                    text_message = f"Oi, {nome}! Tudo bem? Vi que você tem {idade} anos, {seguidores} seguidores e {midias} fotos no fatalmodel."
                    # API_KEY = 'LpTeste'  

                    response = send_message('5521964781930', text_message, API_KEY)
                    
                    print(f"Resposta da API: {response.status_code}")
                    
                    if 200 <= response.status_code < 300:
                        update_lead_status(lead_id, 'Primeiro contato realizado')
                        tempo_espera = random.randint(5, 40)                        
                        
                        # Se não for o primeiro ou o último, acrescenta espera
                        if len(lead_ids) > 1 and index < len(lead_ids) - 1:
                            sleep(tempo_espera)
                            print(f"Esperando {tempo_espera} segundos")
                            
                    else:
                        errors.append(f'Erro ao enviar mensagem para {lead.nome}')
                        print(f"Erro ao enviar mensagem para {lead.nome}: {response.status_code}")
                except Exception as e:
                    errors.append(f'Erro ao processar lead {lead.nome}: {str(e)}')
                    print(f"Erro ao processar lead {lead.nome}: {str(e)}")

            if not errors:
                print("Todas as mensagens foram enviadas com sucesso")
                return JsonResponse({'status': 'Mensagens enviadas com sucesso'})
            else:
                print(f"Ocorreram erros: {errors}")
                return JsonResponse({'status': 'Erros ocorreram', 'errors': errors}, status=500)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {str(e)}")
            return JsonResponse({'status': 'Erro na decodificação do JSON'}, status=400)
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return JsonResponse({'status': 'Erro interno do servidor', 'error': str(e)}, status=500)
    else:
        print("Método não permitido")
        return JsonResponse({'status': 'Método não permitido'}, status=405)
