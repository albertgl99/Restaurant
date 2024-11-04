from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('restaurant/', views.home, name='home'),
    path('restaurant/login/', views.login, name='login'),
    path('restaurant/register/', views.register, name='register'),
    path('restaurant/logout/', views.logout, name='logout'),
    path('restaurant/afegeix-plat/', views.view_afegir_plat, name='afegeix_plat'),
    path('restaurant/plats/', views.llista_plats, name='llista_plats'),
    path('restaurant/eliminar-plat/<str:plat_id>/', views.eliminar_plat, name='eliminar_plat'),
    path('restaurant/modificar-plat/<str:plat_id>/', views.modificar_plat, name='modificar_plat'),
    path('restaurant/mostra-carta-setmanal/', views.mostra_carta_setmanal, name='mostra_carta_setmanal'),
    path('restaurant/carta-aleatoria/', views.carta_aleatoria, name='carta_aleatoria'),
    path('restaurant/seleccionar-carta-setmanal/', views.seleccionar_carta_setmanal, name='seleccionar_carta_setmanal'),

]
