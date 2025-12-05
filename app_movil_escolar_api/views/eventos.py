from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date, time
from app_movil_escolar_api.serializers import EventoAcademicoSerializer
from app_movil_escolar_api.models import EventoAcademico
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
import json


class EventosAcademicosList(generics.ListAPIView):
    """
    GET /eventos-academicos/
    Lista todos los eventos académicos
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        print("=" * 60)
        print("GET /eventos-academicos/")
        print(f"Usuario: {request.user}")
        print("=" * 60)
        
        try:
            eventos = EventoAcademico.objects.select_related('responsable').all()
            serializer = EventoAcademicoSerializer(eventos, many=True)
            
            print(f"Total eventos encontrados: {eventos.count()}")
            
            return Response({
                "eventos": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error al listar eventos: {str(e)}")
            return Response({
                "error": f"Error al obtener eventos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventoAcademicoView(generics.GenericAPIView):
    """
    GET /evento-academico/?id={id} - Obtener evento por ID
    POST /evento-academico/ - Registrar nuevo evento
    PUT /evento-academico/ - Actualizar evento
    DELETE /evento-academico/?id={id} - Eliminar evento
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        """Obtener evento por ID"""
        evento_id = request.query_params.get('id')
        
        print("=" * 60)
        print(f"GET /evento-academico/?id={evento_id}")
        print(f"Usuario: {request.user}")
        print("=" * 60)
        
        if not evento_id:
            return Response({
                "error": "El parámetro 'id' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            evento = EventoAcademico.objects.select_related('responsable').get(id=evento_id)
            serializer = EventoAcademicoSerializer(evento)
            
            print(f"Evento encontrado: {evento.nombre_evento}")
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except EventoAcademico.DoesNotExist:
            print(f"Evento {evento_id} no encontrado")
            return Response({
                "error": "Evento no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Registrar nuevo evento"""
        print("=" * 60)
        print("POST /evento-academico/")
        print(f"Usuario: {request.user}")
        print(f"Datos recibidos: {request.data}")
        print("=" * 60)
        
        # Validar campos requeridos
        errors = self._validate_evento_data(request.data, is_update=False)
        if errors:
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            # Crear evento
            evento = EventoAcademico.objects.create(
                nombre_evento=request.data.get('nombre_evento'),
                tipo_evento=request.data.get('tipo_evento'),
                fecha_realizacion=request.data.get('fecha_realizacion'),
                hora_inicio=request.data.get('hora_inicio'),
                hora_fin=request.data.get('hora_fin'),
                lugar=request.data.get('lugar'),
                publico_objetivo=request.data.get('publico_objetivo'),
                programa_educativo=request.data.get('programa_educativo'),
                responsable_id=request.data.get('responsable'),
                descripcion=request.data.get('descripcion'),
                cupo_maximo=request.data.get('cupo_maximo')
            )
            
            serializer = EventoAcademicoSerializer(evento)
            
            print(f"Evento creado: ID={evento.id}, Nombre={evento.nombre_evento}")
            
            return Response({
                "message": "Evento registrado exitosamente",
                "evento": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error al crear evento: {str(e)}")
            return Response({
                "error": f"Error al registrar evento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Actualizar evento existente"""
        evento_id = request.data.get('id')
        
        print("=" * 60)
        print(f"PUT /evento-academico/")
        print(f"Usuario: {request.user}")
        print(f"ID: {evento_id}")
        print(f"Datos recibidos: {request.data}")
        print("=" * 60)
        
        if not evento_id:
            return Response({
                "error": "El campo 'id' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar campos
        errors = self._validate_evento_data(request.data, is_update=True)
        if errors:
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            evento = EventoAcademico.objects.get(id=evento_id)
            
            # Actualizar campos
            evento.nombre_evento = request.data.get('nombre_evento', evento.nombre_evento)
            evento.tipo_evento = request.data.get('tipo_evento', evento.tipo_evento)
            evento.fecha_realizacion = request.data.get('fecha_realizacion', evento.fecha_realizacion)
            evento.hora_inicio = request.data.get('hora_inicio', evento.hora_inicio)
            evento.hora_fin = request.data.get('hora_fin', evento.hora_fin)
            evento.lugar = request.data.get('lugar', evento.lugar)
            evento.publico_objetivo = request.data.get('publico_objetivo', evento.publico_objetivo)
            evento.programa_educativo = request.data.get('programa_educativo', evento.programa_educativo)
            evento.responsable_id = request.data.get('responsable', evento.responsable_id)
            evento.descripcion = request.data.get('descripcion', evento.descripcion)
            evento.cupo_maximo = request.data.get('cupo_maximo', evento.cupo_maximo)
            
            evento.save()
            
            serializer = EventoAcademicoSerializer(evento)
            
            print(f"Evento {evento_id} actualizado exitosamente")
            
            return Response({
                "message": "Evento actualizado exitosamente",
                "evento": serializer.data
            }, status=status.HTTP_200_OK)
            
        except EventoAcademico.DoesNotExist:
            print(f"Evento {evento_id} no encontrado")
            return Response({
                "error": "Evento no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al actualizar evento: {str(e)}")
            return Response({
                "error": f"Error al actualizar evento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, *args, **kwargs):
        """Eliminar evento"""
        evento_id = request.query_params.get('id')
        
        print("=" * 60)
        print(f"DELETE /evento-academico/?id={evento_id}")
        print(f"Usuario: {request.user}")
        print("=" * 60)
        
        if not evento_id:
            return Response({
                "error": "El parámetro 'id' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            evento = EventoAcademico.objects.get(id=evento_id)
            nombre = evento.nombre_evento
            evento.delete()
            
            print(f"Evento '{nombre}' eliminado exitosamente")
            
            return Response({
                "message": "Evento eliminado exitosamente"
            }, status=status.HTTP_200_OK)
            
        except EventoAcademico.DoesNotExist:
            print(f"Evento {evento_id} no encontrado")
            return Response({
                "error": "Evento no encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al eliminar evento: {str(e)}")
            return Response({
                "error": f"Error al eliminar evento: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _validate_evento_data(self, data, is_update=False):
        """
        Validar datos del evento
        Retorna diccionario de errores o None si todo es válido
        """
        errors = {}
        
        # Validar nombre_evento
        if not data.get('nombre_evento') or not data.get('nombre_evento').strip():
            errors['nombre_evento'] = 'Este campo es requerido'
        
        # Validar tipo_evento
        tipo_evento = data.get('tipo_evento')
        if not tipo_evento:
            errors['tipo_evento'] = 'Este campo es requerido'
        elif tipo_evento not in ['Conferencia', 'Taller', 'Seminario', 'Concurso']:
            errors['tipo_evento'] = 'Tipo de evento no válido'
        
        # Validar fecha_realizacion
        fecha_realizacion = data.get('fecha_realizacion')
        if not fecha_realizacion:
            errors['fecha_realizacion'] = 'Este campo es requerido'
        else:
            try:
                if isinstance(fecha_realizacion, str):
                    fecha_obj = datetime.strptime(fecha_realizacion, '%Y-%m-%d').date()
                else:
                    fecha_obj = fecha_realizacion
                
                if fecha_obj < date.today():
                    errors['fecha_realizacion'] = 'La fecha debe ser mayor o igual a la fecha actual'
            except ValueError:
                errors['fecha_realizacion'] = 'Formato de fecha inválido. Use YYYY-MM-DD'
        
        # Validar hora_inicio
        hora_inicio = data.get('hora_inicio')
        if not hora_inicio:
            errors['hora_inicio'] = 'Este campo es requerido'
        
        # Validar hora_fin
        hora_fin = data.get('hora_fin')
        if not hora_fin:
            errors['hora_fin'] = 'Este campo es requerido'
        
        # Validar que hora_fin > hora_inicio
        if hora_inicio and hora_fin:
            try:
                if isinstance(hora_inicio, str):
                    hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
                else:
                    hora_inicio_obj = hora_inicio
                
                if isinstance(hora_fin, str):
                    hora_fin_obj = datetime.strptime(hora_fin, '%H:%M').time()
                else:
                    hora_fin_obj = hora_fin
                
                if hora_fin_obj <= hora_inicio_obj:
                    errors['hora_fin'] = 'La hora de fin debe ser posterior a la hora de inicio'
            except ValueError:
                errors['hora_inicio'] = 'Formato de hora inválido. Use HH:MM'
        
        # Validar lugar
        if not data.get('lugar') or not data.get('lugar').strip():
            errors['lugar'] = 'Este campo es requerido'
        
        # Validar publico_objetivo
        publico_objetivo = data.get('publico_objetivo')
        if not publico_objetivo:
            errors['publico_objetivo'] = 'Debe seleccionar al menos un público objetivo'
        else:
            # Parsear si es string JSON
            try:
                if isinstance(publico_objetivo, str):
                    publico_list = json.loads(publico_objetivo)
                else:
                    publico_list = publico_objetivo
                
                if not publico_list or len(publico_list) == 0:
                    errors['publico_objetivo'] = 'Debe seleccionar al menos un público objetivo'
                
                # Si incluye "Estudiantes", programa_educativo es obligatorio
                if 'Estudiantes' in publico_list:
                    programa = data.get('programa_educativo')
                    if not programa or not programa.strip():
                        errors['programa_educativo'] = 'Debe seleccionar un programa educativo cuando el público objetivo incluye estudiantes'
            except (json.JSONDecodeError, TypeError):
                errors['publico_objetivo'] = 'Formato de público objetivo inválido'
        
        # Validar responsable
        responsable_id = data.get('responsable')
        if not responsable_id:
            errors['responsable'] = 'Este campo es requerido'
        else:
            try:
                user = User.objects.get(id=responsable_id)
                # Verificar que sea Maestro o Administrador
                if not (user.groups.filter(name='Maestro').exists() or 
                       user.groups.filter(name='Administrador').exists()):
                    errors['responsable'] = 'El responsable debe ser un Maestro o Administrador'
            except User.DoesNotExist:
                errors['responsable'] = 'Usuario responsable no encontrado'
        
        # Validar descripcion
        descripcion = data.get('descripcion')
        if not descripcion or not descripcion.strip():
            errors['descripcion'] = 'Este campo es requerido'
        elif len(descripcion) > 300:
            errors['descripcion'] = 'La descripción no debe exceder 300 caracteres'
        
        # Validar cupo_maximo
        cupo_maximo = data.get('cupo_maximo')
        if not cupo_maximo:
            errors['cupo_maximo'] = 'Este campo es requerido'
        else:
            try:
                cupo = int(cupo_maximo)
                if cupo <= 0:
                    errors['cupo_maximo'] = 'El cupo debe ser mayor a 0'
                elif cupo > 999:
                    errors['cupo_maximo'] = 'El cupo no debe exceder 3 dígitos'
            except (ValueError, TypeError):
                errors['cupo_maximo'] = 'El cupo debe ser un número válido'
        
        return errors if errors else None
