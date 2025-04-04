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
from geojson import Point,Feature, FeatureCollection



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
        User.objects.create_user(username=nombre, password= contraseña, email=mail, tipo=tipo)
        return HttpResponseRedirect('/login')
    
        
"""
Vista para agregar un nuevo restaurante al sistema.

- Si el método es 'GET', se muestra un formulario vacío para registrar un restaurante.
- Si el método es 'POST', se procesa el formulario, procesando para añadir geolocalización y un dueño. 
  Si los datos son válidos, se guarda en la db. Si no lo son, se vuelve a mostrar el formulario.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
from django.http import HttpResponseForbidden

@login_required
def add_restaurant(request):
    # Verificar si el usuario es un propietario
    if request.user.tipo != 'Propietario':
        return HttpResponseForbidden("Solo los propietarios pueden añadir restaurantes.")
    
    if request.method == 'GET':
        form = RestaurantForm()  # Cargar el formulario vacío
        return render(request, 'todoapp/register_restaurant.html', {'form': form})
    elif request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            obj=form.save(commit=False)  # Guardar el restaurante si los datos son válidos
            [lon, lat]=getGeoLoc(obj.address)
            obj.lon=lon  # Asignar longitud y latitud
            obj.lat=lat
            obj.owner = request.user  # Asignar al propietario logeado
            obj.save()
            form.save_m2m()
            return HttpResponseRedirect('/my_restaurants')  # Redirigir a "Mis Restaurantes"

        else:
            return render(request, 'todoapp/register_restaurant.html', {'form': form})


"""
Vista para listar los restaurantes en función de ciertos filtros.

- Se permite filtrar por comuna, categoría y rango de calificación.
- Si no se especifican filtros, se listan todos los restaurantes.
- Los datos de geolocalización de los restaurantes se procesan para mostrarlos en un mapa interactivo.
- Se pasa el listado de comunas y categorías para que sean utilizados como filtros en la interfaz.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
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
        geolocs.append(Feature(
            geometry=Point((float(rest.lon), float(rest.lat))), 
            properties={
                "title": rest.name, 
                "description": rest.address
            }
        ))
    
    gl = FeatureCollection(geolocs)
    

    # Pasar todos los datos al contexto
    return render(request, "todoapp/restaurantes.html", {
        'restaurantes': restaurantes,
        'comunas': comunas,
        'categorias': categorias,  # Incluir categorías en el contexto
        'mapbox_access_token': mapbox_access_token,
        'geojson': gl,
        
    })

"""
Vista para iniciar sesión en el sistema.

- Si el método es 'GET', se muestra el formulario de inicio de sesión.
- Si el método es 'POST', se obtienen las credenciales ingresadas por el usuario y se intenta autenticar.
  Si las credenciales son correctas, se inicia la sesión y redirige al listado de restaurantes.
  Si las credenciales son incorrectas, redirige a la página de registro.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
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
"""
Vista para cerrar sesión en el sistema.

- Finaliza la sesión activa del usuario y redirige al listado de restaurantes.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/restaurant_list')

"""
Vista para mostrar los detalles de un restaurante y permitir añadir reseñas.

- Si el método es 'GET', se cargan los detalles del restaurante y las reseñas asociadas.
- Si el método es 'POST' y el usuario está autenticado, se procesa el formulario para añadir una nueva reseña.
- Se calcula el promedio de calificaciones basado en las reseñas existentes.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
- restaurant_id: ID del restaurante cuyos detalles se mostrarán.
"""

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

"""
Vista para editar o eliminar una reseña.

- Solo el usuario que creó la reseña puede acceder a esta vista.
- Permite editar el comentario y la calificación de una reseña.
- Permite eliminar una reseña y actualizar el promedio del restaurante asociado.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
- review_id: ID de la reseña a editar o eliminar.
"""

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

"""
Función para obtener la geolocalización de una dirección.
- Si se encuentra la dirección, retorna una lista con la longitud y latitud.
- Si ocurre algún error o no se encuentra la dirección, retorna [0, 0].

Argumento:
- address: Una cadena de texto que representa la dirección a geolocalizar.

Retorna:
- Una lista de dos elementos: [longitud, latitud].
"""
def getGeoLoc(address):
    app = Nominatim(user_agent="tutorial")
    try:
        return [app.geocode(address).raw["lon"], app.geocode(address).raw["lat"]]
    except:
        return [0,0]

"""
Vista para listar los restaurantes de un propietario.

- Solo los usuarios de tipo "Propietario" pueden acceder a esta vista.
- Muestra una lista de restaurantes asociados al usuario autenticado.

Argumento:
- request: La solicitud HTTP recibida por el servidor.
"""


@login_required
def my_restaurants(request):
    if request.user.tipo == 'Propietario':
        restaurants = Restaurant.objects.filter(owner=request.user)
        return render(request, 'todoapp/my_restaurants.html', {'restaurants': restaurants})
    else:
        return render(request, 'todoapp/error.html', {'message': 'No tienes acceso a esta página.'})

