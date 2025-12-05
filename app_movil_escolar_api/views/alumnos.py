from django.db.models import *
from django.db import transaction, IntegrityError
from app_movil_escolar_api.serializers import UserSerializer, AlumnoSerializer
from app_movil_escolar_api.models import Alumnos
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.tokens import RefreshToken


class AlumnoAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        print("=" * 60)
        print("PETICIÓN GET /lista-alumnos/")
        print(f"Usuario autenticado: {request.user}")
        print(f"Es autenticado: {request.user.is_authenticated}")
        print("=" * 60)
        
        try:
            alumnos = Alumnos.objects.select_related('user').all()
            print(f"Total alumnos encontrados: {alumnos.count()}")
            
            serializer = AlumnoSerializer(alumnos, many=True)
            print(f"Datos serializados: {len(serializer.data)} registros")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error al obtener alumnos: {str(e)}")
            return Response({'error': str(e)}, status=500)


class AlumnoView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print("=" * 60)
        print("PETICIÓN RECIBIDA EN /alumno/")
        print("Método:", request.method)
        print("Headers:", dict(request.headers))
        print("Datos recibidos:", request.data)
        print("=" * 60)
        
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            role = request.data.get('rol', 'Alumno')
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                print(f"Error: Email {email} ya existe")
                return Response({"email": ["Este email ya está registrado"]}, status=400)
            
            matricula = request.data.get("matricula")
            if Alumnos.objects.filter(matricula=matricula).exists():
                print(f"Error: Matrícula {matricula} ya existe")
                return Response({"matricula": ["Esta matrícula ya existe"]}, status=400)
            
            curp = request.data.get("curp")
            if curp and Alumnos.objects.filter(curp=curp).exists():
                print(f"Error: CURP {curp} ya existe")
                return Response({"curp": ["Este CURP ya está registrado"]}, status=400)

            try:
                print("Datos válidos, creando alumno...")
                
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

                alumno = Alumnos.objects.create(
                    user=user,
                    matricula=request.data.get("matricula"),
                    fecha_nacimiento=request.data.get("fecha_nacimiento"),
                    curp=request.data.get("curp", "").upper() if request.data.get("curp") else None,
                    rfc=request.data.get("rfc", "").upper() if request.data.get("rfc") else None,
                    edad=request.data.get("edad"),
                    telefono=request.data.get("telefono"),
                    ocupacion=request.data.get("ocupacion")
                )
                alumno.save()
                
                print(f"Alumno creado con ID: {alumno.id}")
                return Response({
                    "message": "Alumno registrado exitosamente",
                    "alumno_created_id": alumno.id
                }, status=201)
            
            except IntegrityError as e:
                print(f"Error IntegrityError: {e}")
                return Response(
                    {"message": f"Error de integridad: {str(e)}"},
                    status=400
                )
        else:
            print("Errores de validación:", user.errors)
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class AlumnoEdit(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, DELETE para alumnos por ID
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Alumnos.objects.select_related('user').all()
    serializer_class = AlumnoSerializer
    
    def get(self, request, pk, *args, **kwargs):
        """Obtener alumno por ID"""
        print(f"GET /alumno-edit/{pk}/")
        try:
            alumno = Alumnos.objects.select_related('user').get(pk=pk)
            serializer = AlumnoSerializer(alumno)
            print(f"Alumno encontrado: {alumno.user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Alumnos.DoesNotExist:
            print(f"Alumno {pk} no encontrado")
            return Response({"error": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        """Actualizar alumno"""
        print(f"PUT /alumno-edit/{pk}/")
        print(f"Datos recibidos: {request.data}")
        
        try:
            alumno = Alumnos.objects.select_related('user').get(pk=pk)
            
            if 'first_name' in request.data:
                alumno.user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                alumno.user.last_name = request.data['last_name']
            if 'email' in request.data:
                email = request.data['email']
                if User.objects.filter(email=email).exclude(id=alumno.user.id).exists():
                    return Response({"email": ["Este email ya está registrado"]}, status=400)
                alumno.user.email = email
                alumno.user.username = email
            
            if 'password' in request.data and request.data['password']:
                alumno.user.set_password(request.data['password'])
            
            alumno.user.save()
            
            if 'matricula' in request.data:
                matricula = request.data['matricula']
                if Alumnos.objects.filter(matricula=matricula).exclude(id=pk).exists():
                    return Response({"matricula": ["Esta matrícula ya existe"]}, status=400)
                alumno.matricula = matricula
            
            if 'fecha_nacimiento' in request.data:
                alumno.fecha_nacimiento = request.data['fecha_nacimiento']
            
            if 'curp' in request.data:
                curp = request.data['curp']
                if curp:
                    if Alumnos.objects.filter(curp=curp).exclude(id=pk).exists():
                        return Response({"curp": ["Este CURP ya está registrado"]}, status=400)
                    alumno.curp = curp.upper()
                else:
                    alumno.curp = None
            
            if 'rfc' in request.data:
                alumno.rfc = request.data['rfc'].upper() if request.data['rfc'] else None
            
            if 'edad' in request.data:
                alumno.edad = request.data['edad']
            
            if 'telefono' in request.data:
                alumno.telefono = request.data['telefono']
            
            if 'ocupacion' in request.data:
                alumno.ocupacion = request.data['ocupacion']
            
            alumno.save()
            
            # Generar nuevo token JWT
            refresh = RefreshToken.for_user(alumno.user)
            
            serializer = AlumnoSerializer(alumno)
            response_data = {
                'message': 'Alumno actualizado exitosamente',
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializer.data
            }
            
            print(f"Alumno {pk} actualizado")
            print(f"Nuevo token generado: {str(refresh.access_token)[:50]}...")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Alumnos.DoesNotExist:
            print(f"Alumno {pk} no encontrado")
            return Response({"error": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            print(f"Error IntegrityError: {e}")
            return Response({"error": f"Error de integridad: {str(e)}"}, status=400)
    
    def delete(self, request, pk, *args, **kwargs):
        """Eliminar alumno"""
        print(f"DELETE /alumno-edit/{pk}/")
        
        try:
            alumno = Alumnos.objects.get(pk=pk)
            user = alumno.user
            alumno.delete()
            user.delete()
            
            print(f"Alumno {pk} eliminado")
            return Response({"message": "Alumno eliminado exitosamente"}, status=status.HTTP_200_OK)
            
        except Alumnos.DoesNotExist:
            print(f"Alumno {pk} no encontrado")
            return Response({"error": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
