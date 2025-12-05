from django.contrib import admin
from django.utils.html import format_html
from app_movil_escolar_api.models import *


@admin.register(Administradores)
class AdministradoresAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "clave_admin", "telefono", "rfc", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "clave_admin", "rfc")
    list_filter = ("creation",)

@admin.register(Maestros)
class MaestrosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "clave_maestro", "area_investigacion", "cubiculo", "telefono", "creation")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "clave_maestro", "rfc")
    list_filter = ("area_investigacion", "creation")
    readonly_fields = ("creation", "update")
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Datos del Maestro', {
            'fields': ('clave_maestro', 'fecha_nacimiento', 'telefono', 'rfc', 'cubiculo')
        }),
        ('Información Académica', {
            'fields': ('area_investigacion', 'materias')
        }),
        ('Fechas', {
            'fields': ('creation', 'update')
        }),
    )

@admin.register(Alumnos)
class AlumnosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "matricula", "curp", "edad", "ocupacion", "creation")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "matricula", "curp", "rfc")
    list_filter = ("ocupacion", "creation")
    readonly_fields = ("creation", "update")
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Datos Personales', {
            'fields': ('matricula', 'fecha_nacimiento', 'curp', 'rfc', 'edad', 'telefono')
        }),
        ('Información Adicional', {
            'fields': ('ocupacion',)
        }),
        ('Fechas', {
            'fields': ('creation', 'update')
        }),
    )

