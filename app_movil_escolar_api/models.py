from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin "+self.user.first_name+" "+self.user.last_name

class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    clave_maestro = models.CharField(max_length=255, null=True, blank=True)  # ID de trabajador
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rfc = models.CharField(max_length=13, null=True, blank=True)
    cubiculo = models.CharField(max_length=100, null=True, blank=True)
    area_investigacion = models.CharField(max_length=255, null=True, blank=True)
    materias = models.TextField(null=True, blank=True)  # Se almacena como string separado por comas
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del maestro "+self.user.first_name+" "+self.user.last_name

class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='alumno')
    
    # Campos identificadores
    matricula = models.CharField(max_length=50, unique=True)
    
    # Datos personales
    fecha_nacimiento = models.DateField(null=True, blank=True)
    curp = models.CharField(max_length=18, null=True, blank=True, unique=True)
    rfc = models.CharField(max_length=13, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    
    # Contacto
    telefono = models.CharField(max_length=15, null=True, blank=True)
    
    # Información adicional
    ocupacion = models.CharField(max_length=100, null=True, blank=True)
    
    # Timestamps
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'app_movil_escolar_api_alumnos'
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f"{self.matricula} - {self.user.first_name} {self.user.last_name}"


class EventoAcademico(models.Model):
    TIPOS_EVENTO = [
        ('Conferencia', 'Conferencia'),
        ('Taller', 'Taller'),
        ('Seminario', 'Seminario'),
        ('Concurso', 'Concurso'),
    ]
    
    PROGRAMAS_EDUCATIVOS = [
        ('Ingeniería en Ciencias de la Computación', 'Ingeniería en Ciencias de la Computación'),
        ('Licenciatura en Ciencias de la Computación', 'Licenciatura en Ciencias de la Computación'),
        ('Ingeniería en Tecnologías de la Información', 'Ingeniería en Tecnologías de la Información'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    nombre_evento = models.CharField(max_length=255, null=False, blank=False)
    tipo_evento = models.CharField(max_length=50, choices=TIPOS_EVENTO, null=False, blank=False)
    fecha_realizacion = models.DateField(null=False, blank=False)
    hora_inicio = models.TimeField(null=False, blank=False)
    hora_fin = models.TimeField(null=False, blank=False)
    lugar = models.CharField(max_length=255, null=False, blank=False)
    publico_objetivo = models.TextField(null=False, blank=False)
    programa_educativo = models.CharField(max_length=100, choices=PROGRAMAS_EDUCATIVOS, null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_responsable')
    descripcion = models.TextField(max_length=300, null=False, blank=False)
    cupo_maximo = models.IntegerField(null=False, blank=False)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'app_movil_escolar_api_eventos_academicos'
        verbose_name = 'Evento Académico'
        verbose_name_plural = 'Eventos Académicos'
        ordering = ['-fecha_realizacion', '-hora_inicio']
    
    def __str__(self):
        return f"{self.nombre_evento} - {self.fecha_realizacion}"
