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
    lon = models.CharField(max_length=12)
    lat = models.CharField(max_length=12)

"""
Modelo para representar a un usuario de nuestra aplicación web,
creado en base al modelo `AbstractUser` de Django.

Características añadidas:
- Tipo: Tipo de usuario
    Se elige entre las opciones Cliente y Propietario.
"""

class User(AbstractUser):
    tipo = [('Cliente','Cliente'),('Propietario','Propietario'),]
    tipo = models.CharField(max_length=12,choices=tipo)


"""
Modelo para representar una review de un restaurante
de nuestra aplcación web

- restaurant: Nombre del restaurante.
- user: Usuario que dejó la review.
- comment: Contenido de la review.
- rating: Puntuación del restaurante de 1 a 5 estrellas.
- created_at: Cuando fue creada la review.
"""  
    
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating entre 1 y 5 estrellas
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} - {self.rating} estrellas"
