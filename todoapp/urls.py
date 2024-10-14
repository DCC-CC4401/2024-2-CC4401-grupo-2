from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register_user'),
    path('register_restaurant/', views.add_restaurant, name='register_restaurant'),
    path('restaurant_list', views.restaurant_list, name='restaurant_list'),
    path('login', views.login_user, name='login'),
    path('logout',views.logout_user, name='logout'),
]