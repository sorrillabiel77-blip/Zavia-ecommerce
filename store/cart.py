from decimal import Decimal
from .models import ProductVariant

CART_KEY = 'zavia_cart_v1'

def get_cart(request):
    items = request.session.get(CART_KEY, {})
    if not isinstance(items, dict): return {}
    return items

def cart_lines(request):
    entries = get_cart(request)
    rows, total, count = [], Decimal('0'), 0
    # dados e preços sempre vêm do servidor (nunca da sessão)
    ids = [int(k) for k in entries if str(k).isdigit()]
    valid = ProductVariant.objects.select_related('product').filter(pk__in=ids,active=True,product__active=True)
    for variant in valid:
        quantity = max(1,min(99,int(entries.get(str(variant.id), 1))))
        price = variant.product.effective_price
        subtotal = price * quantity
        rows.append({'variant':variant,'product':variant.product,'quantity':quantity,'subtotal':subtotal,'available':quantity<=variant.stock})
        total += subtotal
        count += quantity
    return rows,total,count

def add_to_cart(request, variant_id, quantity):
    cart = get_cart(request).copy()
    key = str(variant_id)
    cart[key] = max(1,min(99,int(cart.get(key,0)) + quantity))
    request.session[CART_KEY] = cart
    request.session.modified = True

def set_quantity(request,variant_id,quantity):
    cart=get_cart(request).copy()
    if quantity <= 0: cart.pop(str(variant_id),None)
    else: cart[str(variant_id)]=min(99,quantity)
    request.session[CART_KEY]=cart
    request.session.modified=True
