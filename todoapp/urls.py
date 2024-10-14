from django.urls import path
from . import views

urlpatterns = [
    path('tareas', views.tareas, name='mis_tareas'),
    path('register', views.register_user, name='register_user'),
    path('add-restaurant', views.add_restaurant, name='add_restaurant'),
    path('register_restaurant/', views.add_restaurant, name='register_restaurant'),
    path('restaurant_list', views.restaurant_list, name='restaurant_list'),
]