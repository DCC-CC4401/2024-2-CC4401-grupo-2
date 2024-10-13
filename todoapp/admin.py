from django.contrib import admin

# Register your models here.
from todoapp.models import User, Tarea, Restaurant
from categorias.models import Categoria
 
admin.site.register(Categoria)
admin.site.register(User)
admin.site.register(Tarea)
admin.site.register(Restaurant)