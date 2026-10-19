from .cart import get_cart

def cart_summary(request):
    cart = get_cart(request)
    return {'cart_count': sum(max(0,min(99,int(v))) for v in cart.values() if str(v).isdigit())}
