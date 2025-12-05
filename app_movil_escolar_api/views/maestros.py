from django.db.models import *
from django.db import transaction, IntegrityError
from app_movil_escolar_api.serializers import UserSerializer, MaestroSerializer
from app_movil_escolar_api.models import Maestros
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.tokens import RefreshToken


class MaestroAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        print("=" * 60)
        print("PETICIÓN GET /lista-maestros/")
        print(f"Usuario autenticado: {request.user}")
        print(f"Es autenticado: {request.user.is_authenticated}")
        print("=" * 60)
        
        try:
            maestros = Maestros.objects.select_related('user').all()
            print(f"Total maestros encontrados: {maestros.count()}")
            
            serializer = MaestroSerializer(maestros, many=True)
            print(f"Datos serializados: {len(serializer.data)} registros")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error al obtener maestros: {str(e)}")
            return Response({'error': str(e)}, status=500)


class MaestroView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print("=" * 60)
        print("PETICIÓN RECIBIDA EN /maestro/")
        print("Método:", request.method)
        print("Headers:", dict(request.headers))
        print("Datos recibidos:", request.data)
        print("=" * 60)
        
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            role = request.data.get('rol', 'Maestro')
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                print(f"Error: Email {email} ya existe")
                return Response({"message":"Username "+email+", is already taken"}, status=400)

            try:
                print("Datos válidos, creando maestro...")
                
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

                materias_data = request.data.get("materias", "[]")
                
                maestro = Maestros.objects.create(
                    user=user,
                    clave_maestro= request.data.get("clave_maestro"),
                    fecha_nacimiento= request.data.get("fecha_nacimiento"),
                    telefono= request.data.get("telefono"),
                    rfc= request.data.get("rfc", "").upper(),
                    cubiculo= request.data.get("cubiculo"),
                    area_investigacion= request.data.get("area_investigacion"),
                    materias= materias_data
                )
                maestro.save()
                
                print(f"Maestro creado con ID: {maestro.id}")
                return Response({"maestro_created_id": maestro.id }, status=201)
            
            except IntegrityError as e:
                print(f"Error IntegrityError: {e}")
                return Response(
                    {"message": f"Username {email}, is already taken"},
                    status=400
                )
        else:
            print("Errores de validación:", user.errors)
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class MaestroEdit(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Maestros.objects.select_related('user').all()
    serializer_class = MaestroSerializer
    
    def get(self, request, pk, *args, **kwargs):
        """Obtener maestro por ID"""
        print(f"GET /maestro-edit/{pk}/")
        try:
            maestro = Maestros.objects.select_related('user').get(pk=pk)
            serializer = MaestroSerializer(maestro)
            print(f"Maestro encontrado: {maestro.user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Maestros.DoesNotExist:
            print(f"Maestro {pk} no encontrado")
            return Response({"error": "Maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        """Actualizar maestro"""
        print(f"PUT /maestro-edit/{pk}/")
        print(f"Datos recibidos: {request.data}")
        
        try:
            maestro = Maestros.objects.select_related('user').get(pk=pk)
            
            if 'first_name' in request.data:
                maestro.user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                maestro.user.last_name = request.data['last_name']
            if 'email' in request.data:
                maestro.user.email = request.data['email']
                maestro.user.username = request.data['email']
            
            maestro.user.save()
            
            if 'clave_maestro' in request.data:
                maestro.clave_maestro = request.data['clave_maestro']
            if 'fecha_nacimiento' in request.data:
                maestro.fecha_nacimiento = request.data['fecha_nacimiento']
            if 'telefono' in request.data:
                maestro.telefono = request.data['telefono']
            if 'rfc' in request.data:
                maestro.rfc = request.data['rfc'].upper()
            if 'cubiculo' in request.data:
                maestro.cubiculo = request.data['cubiculo']
            if 'area_investigacion' in request.data:
                maestro.area_investigacion = request.data['area_investigacion']
            if 'materias' in request.data:
                maestro.materias = request.data['materias']
            
            maestro.save()
            
            # Generar nuevo token JWT
            refresh = RefreshToken.for_user(maestro.user)
            
            serializer = MaestroSerializer(maestro)
            response_data = {
                'message': 'Maestro actualizado exitosamente',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializer.data
            }
            
            print(f"Maestro {pk} actualizado")
            print(f"Nuevo token generado: {str(refresh.access_token)[:50]}...")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Maestros.DoesNotExist:
            print(f"Maestro {pk} no encontrado")
            return Response({"error": "Maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk, *args, **kwargs):
        """Eliminar maestro"""
        print(f"DELETE /maestro-edit/{pk}/")
        
        try:
            maestro = Maestros.objects.get(pk=pk)
            user = maestro.user
            maestro.delete()
            user.delete()
            
            print(f"Maestro {pk} eliminado")
            return Response({"message": "Maestro eliminado correctamente"}, status=status.HTTP_200_OK)
            
        except Maestros.DoesNotExist:
            print(f"Maestro {pk} no encontrado")
            return Response({"error": "Maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
