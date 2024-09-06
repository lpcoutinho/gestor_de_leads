import csv
from django.core.management.base import BaseCommand
from leads.models import Lead

class Command(BaseCommand):
    help = 'Importa leads de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Caminho para o arquivo CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        self.stdout.write(f"Iniciando a importação do arquivo CSV: {csv_file}")

        try:
            # Primeiro, conte o número total de registros
            with open(csv_file, mode='r', encoding='utf-8') as file:
                total_count = sum(1 for _ in file) - 1  # Subtraímos 1 para ignorar o cabeçalho

            count = 0

            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Atualiza ou cria o Lead no banco de dados
                    Lead.objects.update_or_create(
                        nome=row['Nome'],
                        telefone=row['Telefone'],
                        valor_hora=row['Valor Hora'],
                        midias=row['Mídias'],
                        idade=row['Idade'],
                        seguidores=row['Seguidores'],
                        local=row['Local'],
                        cidade=row['Cidade'],
                        estado=row['Estado'],
                        quem_atende=row['Quem Atende'],
                        url=row['URL']
                    )
                    
                    count += 1
                    # Exibe a cada 100 registros ou no final
                    if count % 100 == 0 or count == total_count:
                        self.stdout.write(f"Registro {count}/{total_count} importado...")

            self.stdout.write(self.style.SUCCESS(f'Importação concluída com sucesso. Total de registros importados: {count}'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'O arquivo {csv_file} não foi encontrado.'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro durante a importação: {e}'))
