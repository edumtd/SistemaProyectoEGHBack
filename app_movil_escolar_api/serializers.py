from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
import json

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

class MaestroSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    
    class Meta:
        model = Maestros
        fields = '__all__'
    
    def to_representation(self, instance):
        """
        Convertir materias a formato array al devolver la respuesta.
        Esto permite que el frontend procese el campo correctamente.
        """
        data = super().to_representation(instance)
        
        if data.get('materias'):
            materias_value = data['materias']
            
            if isinstance(materias_value, str):
                try:
                    data['materias'] = json.loads(materias_value)
                except (json.JSONDecodeError, TypeError):
                    data['materias'] = materias_value.split(',') if ',' in materias_value else []
            elif not isinstance(materias_value, list):
                data['materias'] = []
        else:
            data['materias'] = []
        
        return data

class AlumnoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Alumnos
        fields = '__all__'


class EventoAcademicoSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = EventoAcademico
        fields = '__all__'
    
    def get_responsable_nombre(self, obj):
        """Obtener nombre completo del responsable"""
        if obj.responsable:
            return f"{obj.responsable.first_name} {obj.responsable.last_name}"
        return None
