# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from categorias.models import Categoria
from comunas.models import Comuna
from todoapp.models import Restaurant, Review
from todoapp.forms import RestaurantForm, ReviewForm
from todoapp.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from geopy.geocoders import Nominatim
from geojson import Point,Feature, GeometryCollection, FeatureCollection, GeoJSON

import json

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
        tipo = request.POST['tipo']
        mail = request.POST['mail']

        user = User.objects.create_user(username=nombre, password= contraseña, email=mail, tipo=tipo)
        return HttpResponseRedirect('/login')
    
        
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
            obj=form.save(commit=False)  # Guardar el restaurante si los datos son válidos
            [lon, lat]=getGeoLoc(obj.address)
            obj.lon=lon
            obj.lat=lat
            obj.save()
            return HttpResponseRedirect('/restaurant_list')  # Redirigir a la página de lista de restaurante
        else:
            return render(request, 'todoapp/register_restaurant.html', {'form': form})



def restaurant_list(request):
    comuna_id = request.GET.get('comuna', None)  # Obtener el ID de la comuna del query parameter
    categoria_id = request.GET.get('categoria', None)  # Obtener el ID de la categoría del query parameter
    rating_filter = request.GET.get('rating', None)  # TOmamos el valor de nuestro filtro



    # Filtrar restaurantes por comuna y/o categoría
    if comuna_id:
        restaurantes = Restaurant.objects.filter(comuna_id=comuna_id)  # Filtrar por comuna
    else:
        restaurantes = Restaurant.objects.all()  # Mostrar todos los restaurantes si no hay filtro

    # Filtrar por categoría si se proporciona
    if categoria_id:
        restaurantes = restaurantes.filter(categorias__id=categoria_id)

    if rating_filter:
        if rating_filter == '1-2':
            restaurantes = restaurantes.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=1, avg_rating__lt=2)
        elif rating_filter == '2-3':
            restaurantes = restaurantes.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=2, avg_rating__lt=3)
        elif rating_filter == '3-4':
            restaurantes = restaurantes.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=3, avg_rating__lt=4)
        elif rating_filter == '4-5':
            restaurantes = restaurantes.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=4, avg_rating__lte=5)    

    comunas = Comuna.objects.all()  # Obtener todas las comunas para el filtro
    categorias = Categoria.objects.all()  # Obtener todas las categorías para el filtro
    mapbox_access_token = 'pk.eyJ1Ijoia2xlaW5rZXRhbGxpY2lzIiwiYSI6ImNtM3htOXkxejFmbGsydm85c2RvOWhmMDkifQ.C0w_HJftDbkzi119R-_AvA'
    geolocs=[]
    for rest in restaurantes:
        geolocs.append(Feature(geometry=Point((float(rest.lon), float(rest.lat)))))
    
    gl = FeatureCollection(geolocs)
    

    # Pasar todos los datos al contexto
    return render(request, "todoapp/restaurantes.html", {
        'restaurantes': restaurantes,
        'comunas': comunas,
        'categorias': categorias,  # Incluir categorías en el contexto
        'mapbox_access_token': mapbox_access_token,
        'geojson': gl,
        
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



def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = restaurant.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = ReviewForm()

    return render(request, 'todoapp/restaurant_detail.html', {
        'restaurant': restaurant,
        'reviews': reviews,
        'form': form,
        'average_rating':average_rating
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        if 'save_changes' in request.POST:  # Guardar cambios
            review.comment = request.POST['comment']
            review.rating = request.POST['rating']
            review.save()
            # Actualizar el promedio del restaurante
            review.restaurant.reviews.aggregate_avg = review.restaurant.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            review.restaurant.save()
        elif 'delete_review' in request.POST:  # Borrar reseña
            review.delete()
            # Actualizar el promedio del restaurante
            review.restaurant.reviews.aggregate_avg = review.restaurant.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            review.restaurant.save()
        return redirect('restaurant_detail', restaurant_id=review.restaurant.id)

    form = ReviewForm(instance=review)
    return render(request, 'todoapp/edit_review.html', {
        'review': review,
        'form': form
    })

def getGeoLoc(address):
    app = Nominatim(user_agent="tutorial")
    try:
        return [app.geocode(address).raw["lon"], app.geocode(address).raw["lat"]]
    except:
        return [0, 0]
    