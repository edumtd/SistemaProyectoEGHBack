from django.db.models import *
from app_movil_escolar_api.serializers import *
from app_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Vista de prueba
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def test_view(request):
    print("=" * 80)
    print("TEST VIEW - PETICIÓN RECIBIDA")
    print(f"Método: {request.method}")
    print(f"Datos: {request.data if request.method == 'POST' else 'GET request'}")
    print("=" * 80)
    return Response({'message': 'Test exitoso', 'method': request.method})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    print("=" * 60)
    print("PETICIÓN DE LOGIN RECIBIDA")
    print("Datos recibidos:", request.data)
    print("=" * 60)
    
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        print("Error: Email y password son requeridos")
        return Response({
            'error': 'Email y password son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=email, password=password)
    
    if user is None:
        print(f"Error: Credenciales inválidas para {email}")
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        print(f"Error: Usuario {email} no está activo")
        return Response({
            'error': 'Usuario inactivo'
        }, status=status.HTTP_403_FORBIDDEN)
    
    rol = None
    if user.groups.filter(name='Administrador').exists():
        rol = 'Administrador'
    elif user.groups.filter(name='Maestro').exists():
        rol = 'Maestro'
    elif user.groups.filter(name='Alumno').exists():
        rol = 'Alumno'
    
    refresh = RefreshToken.for_user(user)
    
    response_data = {
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'rol': rol
    }
    
    print("Login exitoso para:", email)
    print("Rol asignado:", rol)
    print("Token generado:", str(refresh.access_token)[:50] + "...")
    
    return Response(response_data, status=status.HTTP_200_OK)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_active:

            roles = user.groups.all()
            role_names = []
            for role in roles:
                role_names.append(role.name)

            profile = Administradores.objects.filter(user=user).first()
            if not profile:
                return Response({},404)

            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'id': user.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'token': token.key,
                'roles': role_names

            })
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({'logout':True})


        return Response({'logout': False})
