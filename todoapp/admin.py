from django.contrib import admin

# Register your models here.
from todoapp.models import User, Restaurant
from categorias.models import Categoria
from comunas.models import Comuna
 
admin.site.register(Categoria)
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Comuna)
