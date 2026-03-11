from django import forms
from pages.models import HomeSlider

class HomeSliderForm(forms.ModelForm):
    class Meta:
        model = HomeSlider
        fields = [
            'image',
            'title',
            'subtitle',
            'button_text',
            'redirect_url',
            'is_active'
        ]