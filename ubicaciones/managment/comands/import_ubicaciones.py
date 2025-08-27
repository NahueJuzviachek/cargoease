from django.core.management.base import BaseCommand
from django.db import transaction
import csv
from ubicaciones.models import Pais, Provincia, Municipio

class Command(BaseCommand):
    help = "Importa provincias y departamentos de Argentina y estados de Brasil desde CSVs."

    def add_arguments(self, parser):
        parser.add_argument("--provincias-arg", required=True, help="Ruta al CSV de provincias Argentina")
        parser.add_argument("--departamentos-arg", required=True, help="Ruta al CSV de departamentos Argentina")
        parser.add_argument("--estados-bra", required=True, help="Ruta al CSV de estados Brasil")

    def handle(self, *args, **options):
        # Crear países
        arg, _ = Pais.objects.get_or_create(codigo_iso="ARG", defaults={"nombre": "Argentina"})
        bra, _ = Pais.objects.get_or_create(codigo_iso="BRA", defaults={"nombre": "Brasil"})

        # Importar provincias ARG
        self.stdout.write("Importando provincias de Argentina...")
        with open(options["provincias_arg"], encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                Provincia.objects.update_or_create(
                    pais=arg,
                    codigo=row['provincia_id'],
                    defaults={'nombre': row['provincia_nombre']}
                )

        # Importar departamentos ARG
        self.stdout.write("Importando departamentos de Argentina...")
        with open(options["departamentos_arg"], encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    provincia = Provincia.objects.get(pais=arg, codigo=row['provincia_id'])
                except Provincia.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"No se encontró la provincia para departamento {row['departamento_nombre']}"))
                    continue
                Municipio.objects.update_or_create(
                    provincia=provincia,
                    codigo=row['departamento_id'],
                    defaults={'nombre': row['departamento_nombre']}
                )

        # Importar estados BRA
        self.stdout.write("Importando estados de Brasil...")
        with open(options["estados_bra"], encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                Provincia.objects.update_or_create(
                    pais=bra,
                    codigo=row['codigo_uf'],
                    defaults={'nombre': row['nome']}
                )

        self.stdout.write(self.style.SUCCESS("Importación completada con éxito."))