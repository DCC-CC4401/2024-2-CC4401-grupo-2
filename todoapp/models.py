from django.db import models
from django.utils import timezone
from categorias.models import Categoria
from comunas.models import Comuna
from django.contrib.auth.models import AbstractUser



"""
Modelo para representar un restaurante en nuestra aplicación web.
A continuación se listan las características que tiene este modelo:

- name: Nombre del restaurante.
- address: Dirección del restaurante .
- phone: Número de teléfono del restaurante .
- email: Correo del restaurante.
- website: Url del sitio web del restaurante .
- description: Descripción del restaurante.
- categorias: Categorías que cumple el restaurante (comida vegana, por ejemplo).
"""
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    email = models.EmailField()
    website = models.URLField()
    description = models.TextField()
    categorias = models.ManyToManyField(Categoria) # Relación muchos a muchos con la tabla categorias
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    
class Tarea(models.Model):  # Todolist able name that inherits models.Model
    titulo = models.CharField(max_length=250)  # un varchar
    contenido = models.TextField(blank=True)  # un text
    fecha_creación = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))  # un date
    categoria = models.ForeignKey(Categoria, default="general", on_delete=models.CASCADE)  # la llave foránea

    def __str__(self):
        return self.titulo  # name to be shown when called

"""
Modelo para representar a un usuario de nuestra aplicación web,
creado en base al modelo `AbstractUser` de Django.

Características añadidas:
- pronombre: Pronombre elegido por el usuario.
    Se elige entre las siguientes opciones: 'La', 'El', 'Le', 'Otro'.
"""

class User(AbstractUser):
    pronombres = [('La','La'),('El','El'),('Le','Le'),('Otro','Otro')]
    pronombre = models.CharField(max_length=5,choices=pronombres)
    

