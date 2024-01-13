from django.urls import path
from . import views

urlpatterns= [
    path('', views.handle_pojazdy),
    
    path('pojazdy/', views.handle_pojazdy),
    path('pojazdy/raport1/', views.get_pojazdy_raport1),
    path('pojazdy/raport2/', views.get_pojazdy_raport2),
    path('pojazdy/raport3/', views.get_pojazdy_raport3),
    path('pojazdy/usun/', views.delete_pojazd),
 
    path('salony/', views.get_salony),
    path('klienci/', views.get_klienci),
    path('pracownicy/', views.get_pracownicy),
    path('faktury/', views.get_faktury),
    path('serwisy/', views.get_serwisy)
]