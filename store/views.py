from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Count
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .cart import add_to_cart, set_quantity, cart_lines
from .forms import RegisterForm
from .models import Category, Product, ProductVariant, Order


def home(request):
    products = Product.objects.filter(active=True).select_related('category').prefetch_related('variants')
    categories = Category.objects.filter(active=True)
    category_slug = request.GET.get('categoria','').strip()
    query = request.GET.get('q','').strip()[:80]
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)
    return render(request,'store/home.html',{'products':products,'categories':categories,'selected_category':category_slug,'search':query})


def detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('variants','gallery'),slug=slug,active=True)
    variants = product.variants.filter(active=True)
    return render(request,'store/product.html',{'product':product,'variants':variants})

@require_POST
def cart_add(request):
    variant_id = request.POST.get('variant_id')
    try:
        quantity = int(request.POST.get('quantity','1'))
    except ValueError:
        return HttpResponseBadRequest('Quantidade inválida')
    if not variant_id or not str(variant_id).isdigit() or quantity < 1 or quantity > 99:
        return HttpResponseBadRequest('Variação ou quantidade inválida')
    variant = get_object_or_404(ProductVariant.objects.select_related('product'),id=int(variant_id),active=True,product__active=True)
    # No pagamento, estoque deve ser verificado novamente dentro de transação.
    current = int(request.session.get('zavia_cart_v1',{}).get(str(variant.id),0))
    if current + quantity > variant.stock:
        messages.error(request,'Não há unidades suficientes desta variação no estoque.')
        return redirect(variant.product.get_absolute_url())
    add_to_cart(request,variant.id,quantity)
    messages.success(request,'Produto adicionado ao carrinho!')
    return redirect('cart')


def cart(request):
    lines,total,count=cart_lines(request)
    return render(request,'store/cart.html',{'lines':lines,'total':total,'count':count})

@require_POST
def cart_update(request):
    try:
        variant_id = int(request.POST.get('variant_id',''))
        quantity = int(request.POST.get('quantity',''))
    except ValueError: return HttpResponseBadRequest('Parâmetros inválidos')
    if quantity > 99 or quantity < 0: return HttpResponseBadRequest('Quantidade inválida')
    set_quantity(request,variant_id,quantity)
    return redirect('cart')


def register(request):
    if request.user.is_authenticated: return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user=form.save()
        login(request,user)
        messages.success(request,'Sua conta ZÁVIA foi criada!')
        return redirect('home')
    return render(request,'store/register.html',{'form':form})

@login_required
def profile(request):
    orders=Order.objects.filter(user=request.user)[:30]
    return render(request,'store/profile.html',{'orders':orders})


def checkout(request):
    lines,total,count=cart_lines(request)
    return render(request,'store/checkout.html',{'lines':lines,'total':total,'count':count})

@staff_member_required
def dashboard(request):
    products=Product.objects.count()
    variants=ProductVariant.objects.count()
    stock=ProductVariant.objects.aggregate(t=Sum('stock'))['t'] or 0
    low_stock=ProductVariant.objects.select_related('product').filter(stock__lte=3).order_by('stock')[:12]
    orders=Order.objects.count()
    return render(request,'store/dashboard.html',{'products_count':products,'variants_count':variants,'stock_count':stock,'orders_count':orders,'low_stock':low_stock})


def health(request):
    return HttpResponse('ok',content_type='text/plain')
