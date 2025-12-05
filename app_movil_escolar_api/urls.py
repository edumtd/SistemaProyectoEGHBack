from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from app_movil_escolar_api.views import bootstrap
from app_movil_escolar_api.views import users
from app_movil_escolar_api.views import maestros
from app_movil_escolar_api.views import alumnos
from app_movil_escolar_api.views import auth
from app_movil_escolar_api.views import eventos


urlpatterns = [
    path('test/', auth.test_view, name='test'),  # Vista de prueba
    path('login/', auth.login_view, name='login'),
    
    path('api/administrador/registro/', users.AdminView.as_view()),
    path('api/administrador/', users.AdminAll.as_view()),
    path('administrador-edit/<int:pk>/', users.AdminEdit.as_view()),
    
    path('api/maestro/registro/', maestros.MaestroView.as_view()),
    path('api/maestro/', maestros.MaestroAll.as_view()),
    path('maestro-edit/<int:pk>/', maestros.MaestroEdit.as_view()),
    
    path('api/alumno/registro/', alumnos.AlumnoView.as_view()),
    path('api/alumno/', alumnos.AlumnoAll.as_view()),
    path('alumno-edit/<int:pk>/', alumnos.AlumnoEdit.as_view()),
    
    path('admin/', users.AdminView.as_view()),
    path('lista-admins/', users.AdminAll.as_view()),
    path('maestro/', maestros.MaestroView.as_view()),
    path('lista-maestros/', maestros.MaestroAll.as_view()),
    path('alumno/', alumnos.AlumnoView.as_view()),
    path('lista-alumnos/', alumnos.AlumnoAll.as_view()),
    
    path('total-users/', users.TotalUsers.as_view(), name='total-users'),
    
    path('eventos-academicos/', eventos.EventosAcademicosList.as_view(), name='eventos-academicos-list'),
    path('evento-academico/', eventos.EventoAcademicoView.as_view(), name='evento-academico'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
