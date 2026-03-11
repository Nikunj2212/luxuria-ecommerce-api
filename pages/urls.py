from django.urls import path
from . import views
from .views import home
from contact.views import contact_view 
from django.urls import path, include




urlpatterns = [
    path('', home, name='home'),
    path('about/', views.about, name='about'),
    path("contact/", contact_view, name="contact_page"),
    path('contact/success/', views.contact_success, name='contact_success'),
    path('collection/', views.collection, name='collection'),
    
]
