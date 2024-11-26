from django import forms
from .models import Restaurant, Review

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'phone', 'email', 'website', 'description', 'categorias', 'comuna']
        exclude = ["lon", "lat"]
        labels = {
            'name': 'Nombre del Restaurante',
            'address': 'Dirección',
            'phone': 'Teléfono',
            'email': 'Correo Electrónico',
            'website': 'Sitio Web',
            'description': 'Descripción',
            'categorias': 'Categorías',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating']
        labels = {
            'rating': 'Puntuación',
            'comment': 'Comentario',
        }