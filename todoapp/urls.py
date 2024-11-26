from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register_user'),
    path('register_restaurant/', views.add_restaurant, name='register_restaurant'),
    path('restaurant_list', views.restaurant_list, name='restaurant_list'),
    path('login', views.login_user, name='login'),
    path('logout',views.logout_user, name='logout'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('my_restaurants/', views.my_restaurants, name='my_restaurants'),
    path('', views.restaurant_list, name='restaurant_list')
]