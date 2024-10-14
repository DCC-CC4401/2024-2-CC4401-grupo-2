# Create your views here.
from django.shortcuts import render, redirect
from categorias.models import Categoria
from comunas.models import Comuna
from todoapp.models import Restaurant
from todoapp.forms import RestaurantForm
from todoapp.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login,logout


"""
Vista para registrar un nuevo usuario en el sistema.

- Si el método es 'GET', se muestra el formulario de registro de usuario.
- Si el método es 'POST', se obtiene la información del formulario y 
  se crea un nuevo usuario con los datos proporcionados (nombre, contraseña, pronombre y correo electrónico).

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
def register_user(request):
    if request.method == 'GET':
        return render(request, "todoapp/register.html")
    elif request.method == 'POST':
        nombre = request.POST['nombre']
        contraseña = request.POST['contraseña']
        pronombre = request.POST['pronombre']
        mail = request.POST['mail']

        user = User.objects.create_user(username=nombre, password= contraseña, email=mail, pronombre=pronombre)
        return HttpResponseRedirect('/restaurant_list')
    
        
"""
Vista para agregar un nuevo restaurante al sistema.

- Si el método es 'GET', se muestra un formulario vacío para registrar un restaurante.
- Si el método es 'POST', se procesa el formulario y se guarda la información del restaurante 
  si los datos son válidos. Si no lo son, se vuelve a mostrar el formulario.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
def add_restaurant(request):
    if request.method == 'GET':
        form = RestaurantForm()  # Cargar el formulario vacío
        return render(request, 'todoapp/register_restaurant.html', {'form': form})
    elif request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el restaurante si los datos son válidos
            return HttpResponseRedirect('/restaurant_list')  # Redirigir a la página de lista de restaurante
        else:
            return render(request, 'todoapp/register_restaurant.html', {'form': form})



def restaurant_list(request):
    comuna_id = request.GET.get('comuna', None)  # Obtener el ID de la comuna del query parameter
    categoria_id = request.GET.get('categoria', None)  # Obtener el ID de la categoría del query parameter

    # Filtrar restaurantes por comuna y/o categoría
    if comuna_id:
        restaurantes = Restaurant.objects.filter(comuna_id=comuna_id)  # Filtrar por comuna
    else:
        restaurantes = Restaurant.objects.all()  # Mostrar todos los restaurantes si no hay filtro

    # Filtrar por categoría si se proporciona
    if categoria_id:
        restaurantes = restaurantes.filter(categorias__id=categoria_id)

    comunas = Comuna.objects.all()  # Obtener todas las comunas para el filtro
    categorias = Categoria.objects.all()  # Obtener todas las categorías para el filtro

    # Pasar todos los datos al contexto
    return render(request, "todoapp/restaurantes.html", {
        'restaurantes': restaurantes,
        'comunas': comunas,
        'categorias': categorias,  # Incluir categorías en el contexto
    })


def login_user(request):
    if request.method == 'GET':
        return render(request,"todoapp/login.html")
    if request.method == 'POST':
        username = request.POST['username']
        contraseña = request.POST['contraseña']
        usuario = authenticate(username=username,password=contraseña)
        if usuario is not None:
            login(request,usuario)
            return HttpResponseRedirect('/restaurant_list')
        else:
            return HttpResponseRedirect('/register')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/restaurant_list')