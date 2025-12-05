from django.db.models import *
from django.db import transaction, IntegrityError
from app_movil_escolar_api.serializers import UserSerializer, AdminSerializer, MaestroSerializer, AlumnoSerializer
from app_movil_escolar_api.models import Administradores, Maestros, Alumnos
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.tokens import RefreshToken
import json


class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        print("=" * 60)
        print("PETICIÓN GET /lista-admins/")
        print(f"Usuario autenticado: {request.user}")
        print(f"Es autenticado: {request.user.is_authenticated}")
        print("=" * 60)
        
        try:
            administradores = Administradores.objects.select_related('user').all()
            print(f"Total administradores encontrados: {administradores.count()}")
            
            serializer = AdminSerializer(administradores, many=True)
            print(f"Datos serializados: {len(serializer.data)} registros")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error al obtener administradores: {str(e)}")
            return Response({'error': str(e)}, status=500)


class AdminView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminEdit(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, DELETE para administradores por ID
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Administradores.objects.select_related('user').all()
    serializer_class = AdminSerializer
    
    def get(self, request, pk, *args, **kwargs):
        """Obtener administrador por ID"""
        print(f"GET /administrador-edit/{pk}/")
        try:
            admin = Administradores.objects.select_related('user').get(pk=pk)
            serializer = AdminSerializer(admin)
            print(f"Administrador encontrado: {admin.user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Administradores.DoesNotExist:
            print(f"Administrador {pk} no encontrado")
            return Response({"error": "Administrador no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        """Actualizar administrador"""
        print(f"PUT /administrador-edit/{pk}/")
        print(f"Datos recibidos: {request.data}")
        
        try:
            admin = Administradores.objects.select_related('user').get(pk=pk)
            
            if 'first_name' in request.data:
                admin.user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                admin.user.last_name = request.data['last_name']
            if 'email' in request.data:
                admin.user.email = request.data['email']
                admin.user.username = request.data['email']
            
            admin.user.save()
            
            if 'clave_admin' in request.data:
                admin.clave_admin = request.data['clave_admin']
            if 'telefono' in request.data:
                admin.telefono = request.data['telefono']
            if 'rfc' in request.data:
                admin.rfc = request.data['rfc'].upper()
            if 'edad' in request.data:
                admin.edad = request.data['edad']
            if 'ocupacion' in request.data:
                admin.ocupacion = request.data['ocupacion']
            
            admin.save()
            
            # Generar nuevo token JWT
            refresh = RefreshToken.for_user(admin.user)
            
            serializer = AdminSerializer(admin)
            response_data = {
                'message': 'Administrador actualizado exitosamente',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializer.data
            }
            
            print(f"Administrador {pk} actualizado")
            print(f"Nuevo token generado: {str(refresh.access_token)[:50]}...")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Administradores.DoesNotExist:
            print(f"Administrador {pk} no encontrado")
            return Response({"error": "Administrador no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk, *args, **kwargs):
        """Eliminar administrador"""
        print(f"DELETE /administrador-edit/{pk}/")
        
        try:
            admin = Administradores.objects.get(pk=pk)
            user = admin.user
            admin.delete()
            user.delete()
            
            print(f"Administrador {pk} eliminado")
            return Response({"message": "Administrador eliminado correctamente"}, status=status.HTTP_200_OK)
            
        except Administradores.DoesNotExist:
            print(f"Administrador {pk} no encontrado")
            return Response({"error": "Administrador no encontrado"}, status=status.HTTP_404_NOT_FOUND)


class TotalUsers(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        # TOTAL ADMINISTRADORES
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # TOTAL MAESTROS
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestroSerializer(maestros_qs, many=True).data

        # Convertir materias_json solo si existen maestros
        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []

        total_maestros = maestros_qs.count()

        # TOTAL ALUMNOS
        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        # Respuesta final
        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )

