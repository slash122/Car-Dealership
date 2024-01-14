from django.urls import path
from . import views

urlpatterns= [
    path('', views.handle_pojazdy),
    
    path('pojazdy/', views.handle_pojazdy),
    path('pojazdy/raport1/', views.get_pojazdy_raport1),
    path('pojazdy/raport2/', views.get_pojazdy_raport2),
    path('pojazdy/raport3/', views.get_pojazdy_raport3),
    path('pojazdy/usun/', views.delete_pojazd),
 
    path('salony/', views.handle_salony),
    path('salony/usun/', views.delete_salon),
    
    path('pracownicy/', views.handle_pracownicy),
    path('pracownicy/usun/', views.delete_pracownik),

    path('klienci/', views.handle_klienci),
    path('klienci/usun/', views.delete_klient),
    
    path('faktury/', views.handle_faktury),
    path('faktury/faktura-pojazd/', views.handle_faktura_pojazd),
    path('faktury/faktura-cena/', views.get_faktura_wartosc),
    path('faktury/usun/', views.delete_faktura),
    
    path('serwisy/', views.handle_serwisy),
    path('serwisy/usun/', views.delete_serwis),
]