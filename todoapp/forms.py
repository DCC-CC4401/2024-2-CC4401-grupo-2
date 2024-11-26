from django import forms
from .models import Restaurant, Review

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'phone', 'email', 'website', 'description', 'categorias', 'comuna']
        exclude = ["lon", "lat"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating']