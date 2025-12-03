from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventario.models import Rubro, Bien


class Command(BaseCommand):
    help = 'Crear grupos de permisos basados en los rubros existentes'

    def handle(self, *args, **options):
        # Obtener el ContentType para el modelo Bien
        bien_content_type = ContentType.objects.get_for_model(Bien)

        # Obtener todos los rubros
        rubros = Rubro.objects.all()

        self.stdout.write(f'Encontrados {rubros.count()} rubros. Creando grupos...')

        for rubro in rubros:
            # Crear nombre del grupo
            group_name = f"Rubro: {rubro.nombre}"

            # Verificar si el grupo ya existe
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(f'Creando grupo: {group_name}')

                # Obtener permisos relacionados con bienes
                # Por ahora, asignamos permisos básicos de visualización
                # En el futuro se pueden agregar permisos más específicos
                permissions = Permission.objects.filter(
                    content_type=bien_content_type,
                    codename__in=[
                        'view_bien',  # Ver bienes
                        'add_bien',   # Agregar bienes
                        'change_bien', # Modificar bienes
                        'delete_bien', # Eliminar bienes
                    ]
                )

                # Asignar permisos al grupo
                group.permissions.add(*permissions)

                self.stdout.write(f'  Permisos asignados: {[p.codename for p in permissions]}')
            else:
                self.stdout.write(f'Grupo ya existe: {group_name}')

        self.stdout.write(self.style.SUCCESS('Grupos de rubros creados exitosamente!'))

        # Mostrar resumen
        total_groups = Group.objects.filter(name__startswith='Rubro: ').count()
        self.stdout.write(f'Total de grupos de rubros: {total_groups}')