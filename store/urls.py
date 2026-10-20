from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('produto/<slug:slug>/',views.detail,name='product_detail'),
    path('fotos/produto/<int:image_id>/',views.product_image,name='product_image'),
    path('carrinho/',views.cart,name='cart'),
    path('carrinho/adicionar/',views.cart_add,name='cart_add'),
    path('carrinho/atualizar/',views.cart_update,name='cart_update'),
    path('cadastro/',views.register,name='register'),
    path('minha-conta/',views.profile,name='profile'),
    path('finalizar/',views.payment_checkout,name='checkout'),
    path('pagamento/retorno/<int:order_id>/',views.payment_return,name='payment_return'),
    path('pagamento/webhook/',views.payment_webhook,name='payment_webhook'),
    path('painel/',views.dashboard,name='dashboard'),
    path('health/',views.health,name='health'),
]
