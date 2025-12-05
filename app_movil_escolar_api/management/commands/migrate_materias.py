from django.core.management.base import BaseCommand
from app_movil_escolar_api.models import Maestros
import json

class Command(BaseCommand):
    help = 'Migra el campo materias de formato CSV a JSON string'

    def handle(self, *args, **options):
        maestros = Maestros.objects.all()
        total = maestros.count()
        migrados = 0
        sin_cambios = 0
        errores = 0

        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING('INICIANDO MIGRACIÓN DE CAMPO MATERIAS'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))
        self.stdout.write(f'Total de maestros: {total}\n')

        for maestro in maestros:
            try:
                if not maestro.materias:
                    maestro.materias = '[]'
                    maestro.save()
                    migrados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Maestro {maestro.id} ({maestro.user.first_name}): NULL → []'
                        )
                    )
                    continue

                materias_value = maestro.materias

                # Verificar si ya es JSON válido
                if isinstance(materias_value, str):
                    try:
                        json.loads(materias_value)
                        sin_cambios += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'⏭️  Maestro {maestro.id} ({maestro.user.first_name}): '
                                f'Ya es JSON válido'
                            )
                        )
                        continue
                    except json.JSONDecodeError:
                        pass

                # Convertir CSV a JSON array
                if ',' in materias_value:
                    materias_list = [
                        materia.strip() 
                        for materia in materias_value.split(',') 
                        if materia.strip()
                    ]
                    maestro.materias = json.dumps(materias_list)
                    maestro.save()
                    migrados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Maestro {maestro.id} ({maestro.user.first_name}): '
                            f'"{materias_value}" → {maestro.materias}'
                        )
                    )
                else:
                    maestro.materias = json.dumps([materias_value.strip()])
                    maestro.save()
                    migrados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Maestro {maestro.id} ({maestro.user.first_name}): '
                            f'"{materias_value}" → {maestro.materias}'
                        )
                    )

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error en maestro {maestro.id}: {str(e)}'
                    )
                )

        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING('RESUMEN DE MIGRACIÓN'))
        self.stdout.write(self.style.WARNING(f'{"="*60}'))
        self.stdout.write(f'Total procesados: {total}')
        self.stdout.write(self.style.SUCCESS(f'✅ Migrados: {migrados}'))
        self.stdout.write(self.style.SUCCESS(f'⏭️  Sin cambios: {sin_cambios}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errores: {errores}'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))
