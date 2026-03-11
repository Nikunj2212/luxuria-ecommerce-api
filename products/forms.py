from django import forms
from .models import Product
from .models import ProductReview

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category', 'subcategory', 'image']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Star") for i in range(1,6)]),
            'review': forms.Textarea(attrs={'rows':3})
        }