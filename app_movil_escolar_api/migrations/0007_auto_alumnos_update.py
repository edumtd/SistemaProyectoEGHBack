# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_movil_escolar_api', '0006_alumnos'),
    ]

    operations = [
        # Eliminar campos antiguos
        migrations.RemoveField(
            model_name='alumnos',
            name='carrera',
        ),
        migrations.RemoveField(
            model_name='alumnos',
            name='semestre',
        ),
        migrations.RemoveField(
            model_name='alumnos',
            name='grupo',
        ),
        
        # Agregar nuevos campos
        migrations.AddField(
            model_name='alumnos',
            name='curp',
            field=models.CharField(blank=True, max_length=18, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='rfc',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='edad',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alumnos',
            name='ocupacion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        
        # Hacer matricula único (ya no permite NULL en el modelo pero en DB sí)
        migrations.AlterField(
            model_name='alumnos',
            name='matricula',
            field=models.CharField(max_length=50, unique=True),
        ),
        
        # Actualizar related_name del user
        migrations.AlterField(
            model_name='alumnos',
            name='user',
            field=models.OneToOneField(on_delete=models.CASCADE, related_name='alumno', to='auth.user'),
        ),
        
        # Actualizar update field
        migrations.AlterField(
            model_name='alumnos',
            name='update',
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
    ]
