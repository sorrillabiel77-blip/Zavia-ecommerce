from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('produto/<slug:slug>/',views.detail,name='product_detail'),
    path('carrinho/',views.cart,name='cart'),
    path('carrinho/adicionar/',views.cart_add,name='cart_add'),
    path('carrinho/atualizar/',views.cart_update,name='cart_update'),
    path('cadastro/',views.register,name='register'),
    path('minha-conta/',views.profile,name='profile'),
    path('finalizar/',views.checkout,name='checkout'),
    path('painel/',views.dashboard,name='dashboard'),
    path('health/',views.health,name='health'),
]
