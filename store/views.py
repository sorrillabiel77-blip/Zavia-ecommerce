from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Count, Prefetch
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .cart import add_to_cart, set_quantity, cart_lines
from .forms import RegisterForm
from .models import Category, Product, ProductVariant, ProductImage, Order


def home(request):
    products = Product.objects.filter(active=True).select_related('category').prefetch_related('variants', Prefetch('gallery', queryset=ProductImage.objects.defer('photo_data')))
    categories = Category.objects.filter(active=True)
    category_slug = request.GET.get('categoria','').strip()
    query = request.GET.get('q','').strip()[:80]
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)
    return render(request,'store/home.html',{'products':products,'categories':categories,'selected_category':category_slug,'search':query})


def detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('variants', Prefetch('gallery', queryset=ProductImage.objects.defer('photo_data'))),slug=slug,active=True)
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
    lines, total, count = cart_lines(request)
    shipping = fixed_shipping_amount()
    return render(request, 'store/cart.html', {
        'lines': lines,
        'total': total,
        'count': count,
        'shipping': shipping,
        'shipping_configured': shipping is not None,
        'total_with_shipping': total + shipping if shipping is not None else None,
    })

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
    return redirect('payment_checkout')

@staff_member_required
@require_http_methods(['GET', 'POST'])
def dashboard(request):
    """Painel visual de operação: não confundir pedidos com faturamento liquidado."""
    if request.method == 'POST':
        if not request.user.has_perm('store.change_product'):
            return HttpResponse(status=403)
        action = request.POST.get('action', '')
        if action == 'archive_demos':
            updated = Product.objects.filter(is_demo=True, active=True).update(active=False, featured=False)
            messages.success(request, f'{updated} produto(s) fictício(s) retirado(s) da vitrine. Nenhum pedido foi apagado.')
        else:
            messages.error(request, 'Ação administrativa não reconhecida.')
        return redirect('dashboard')

    paid_states = ('paid', 'preparing', 'shipped', 'delivered')
    product_qs = Product.objects.all()
    stats = {
        'products_count': product_qs.count(),
        'active_products_count': product_qs.filter(active=True, is_demo=False).count(),
        'demo_count': product_qs.filter(is_demo=True, active=True).count(),
        'archived_count': product_qs.filter(active=False).count(),
        'variants_count': ProductVariant.objects.count(),
        'stock_count': ProductVariant.objects.filter(active=True, product__active=True, product__is_demo=False).aggregate(t=Sum('stock'))['t'] or 0,
        'orders_count': Order.objects.count(),
        'pending_count': Order.objects.filter(status='pending_payment').count(),
        'paid_count': Order.objects.filter(status__in=paid_states).count(),
        'paid_order_amount': Order.objects.filter(status__in=paid_states).aggregate(t=Sum('total'))['t'] or 0,
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:8],
        'low_stock': ProductVariant.objects.select_related('product').filter(active=True, product__active=True, product__is_demo=False, stock__lte=3).order_by('stock')[:10],
    }
    return render(request, 'store/dashboard.html', stats)


@require_http_methods(['GET'])
def product_image(request, image_id):
    """Serve arquivo WebP realmente enviado. Nunca depende de disco temporário."""
    photo = get_object_or_404(ProductImage.objects.select_related('product').only('photo_data', 'has_upload', 'product__active'), pk=image_id, has_upload=True)
    # Admin pode conferir fotos enquanto cadastra produtos ainda não publicados.
    if not photo.product.active and not request.user.is_staff:
        raise Http404('Foto não publicada')
    if not photo.photo_data:
        raise Http404('Foto não encontrada')
    response = HttpResponse(bytes(photo.photo_data), content_type='image/webp')
    response['Cache-Control'] = 'public, max-age=300'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def health(request):
    return HttpResponse('ok',content_type='text/plain')

# ---------------- InfinitePay Checkout Integrado ----------------
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .cart import CART_KEY
from .checkout_forms import CheckoutForm
from .models import OrderItem
from .infinitepay import create_payment_link, InfinitePayError, verify_and_apply, order_reference


def fixed_shipping_amount():
    """Obtém o frete fixo, independentemente de o pagamento estar habilitado."""
    try:
        fixed = Decimal(str(settings.ZAVIA_SHIPPING_FLAT).replace(',', '.')).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not fixed.is_finite() or fixed < 0 or fixed > 1000:
        return None
    return fixed


def checkout_ready():
    fixed = fixed_shipping_amount()
    ready = (fixed is not None and bool(settings.INFINITEPAY_API_KEY)
             and bool(settings.INFINITEPAY_TAG) and settings.ZAVIA_CHECKOUT_ENABLED)
    return bool(ready), fixed


@login_required
def payment_checkout(request):
    lines, subtotal, count = cart_lines(request)
    ready, shipping = checkout_ready()
    if not lines:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart')
    if not ready:
        return render(request, 'store/checkout.html', {'configured': False, 'lines':lines, 'total':subtotal, 'shipping':shipping, 'shipping_configured':shipping is not None, 'total_with_shipping':subtotal + shipping if shipping is not None else None})
    if any(not x['available'] or x['product'].is_demo for x in lines):
        messages.error(request, 'Confira o estoque. Produtos ilustrativos não podem ser vendidos.')
        return redirect('cart')
    if not request.session.get('zavia_checkout_nonce'):
        request.session['zavia_checkout_nonce'] = uuid.uuid4().hex
    initial = {'full_name': request.user.get_full_name() or request.user.username, 'email': request.user.email}
    form = CheckoutForm(request.POST or None, initial=initial)
    grand_total = subtotal + shipping
    if request.method == 'POST' and form.is_valid():
        nonce = request.POST.get('nonce', '')
        if not nonce or nonce != request.session.get('zavia_checkout_nonce'):
            messages.error(request, 'Recarregue o checkout para confirmar seu pedido.')
            return redirect('payment_checkout')
        # HTTP externo sempre fora da transação; reserva de estoque com row locks no PostgreSQL.
        order = None
        with transaction.atomic():
            # Bloqueio por cliente + nonce para impedir dupla reserva em POST simultâneo.
            from django.contrib.auth import get_user_model
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            existing = Order.objects.filter(checkout_nonce=nonce).first()
            if existing:
                messages.warning(request, 'Esse pedido já está registrado. Confira a situação antes de tentar novamente.')
                return redirect('payment_return', order_id=existing.pk)
            ids = sorted(x['variant'].pk for x in lines)
            locked = {v.pk: v for v in ProductVariant.objects.select_for_update().select_related('product').filter(pk__in=ids)}
            current_lines = []
            for row in lines:
                variant = locked.get(row['variant'].pk)
                if not variant or not variant.active or not variant.product.active or variant.product.is_demo or variant.stock < row['quantity']:
                    messages.error(request, 'Uma peça ficou indisponível. Atualize seu carrinho.')
                    return redirect('cart')
                current_lines.append((variant, row['quantity'], variant.product.effective_price))
            real_subtotal = sum((p * qty for v, qty, p in current_lines), Decimal('0'))
            order = Order.objects.create(user=request.user, checkout_nonce=nonce,
                customer_name=form.cleaned_data['full_name'], contact_email=form.cleaned_data['email'],
                address=f"Telefone: {form.cleaned_data['phone']}\n{form.cleaned_address()}",
                shipping_amount=shipping, total=real_subtotal + shipping,
                payment_status='awaiting_payment', stock_reserved=True,
                payment_expires_at=timezone.now() + timedelta(minutes=30))
            for variant, qty, price in current_lines:
                ProductVariant.objects.filter(pk=variant.pk).update(stock=F('stock')-qty)
                OrderItem.objects.create(order=order, variant=variant,
                    description=f'{variant.product.name} — {variant.color}, {variant.size}',
                    sku=variant.sku, quantity=qty, unit_price=price)
        request.session.pop('zavia_checkout_nonce', None)
        try:
            base_url = request.build_absolute_uri('/').rstrip('/')
            pref_id, redirect_url = create_payment_link(order, base_url)
        except InfinitePayError:
            # Um timeout não comprova que a InfinitePay NÃO criou o link.
            # Preserva-se a reserva para conferência manual: não duplicar venda de SKU.
            Order.objects.filter(pk=order.pk, status='pending_payment').update(payment_status='link_creation_uncertain')
            messages.error(request, 'Não foi possível confirmar a criação do pagamento. Pedido em revisão; nenhuma nova cobrança será iniciada automaticamente.')
            return redirect('payment_return', order_id=order.pk)
        order.gateway_preference_id = pref_id
        order.gateway_checkout_url = redirect_url
        order.save(update_fields=['gateway_preference_id', 'gateway_checkout_url'])
        request.session.pop(CART_KEY, None)
        return redirect(redirect_url)
    return render(request, 'store/checkout.html',
                  {'configured': True, 'lines': lines, 'subtotal': subtotal,
                   'shipping': shipping, 'total': grand_total,
                   'form': form, 'nonce': request.session['zavia_checkout_nonce'],
                   'checkout_provider':'InfinitePay'})


@login_required
@require_GET
def payment_return(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    # Nunca confiar somente em parâmetros de retorno. Consulta autenticada à InfinitePay.
    transaction_nsu = request.GET.get('transaction_nsu', '')
    slug = request.GET.get('slug', '')
    order_nsu = request.GET.get('order_nsu', '')
    if order_nsu == order_reference(order.pk) and transaction_nsu and slug:
        try:
            verify_and_apply(order.pk, transaction_nsu, slug)
            order.refresh_from_db()
        except InfinitePayError:
            pass  # O webhook/reconciliação poderá confirmar posteriormente.
    return render(request, 'store/payment_return.html', {'order': order})


@csrf_exempt
@require_POST
def payment_webhook(request):
    # Não confiar no corpo: validar pagamento via API autenticada antes de qualquer alteração.
    if len(request.body) > 16000:
        return HttpResponse(status=413)
    try:
        import json
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)
    if not isinstance(payload, dict):
        return HttpResponse(status=400)
    nsu = payload.get('order_nsu', '')
    transaction_nsu = payload.get('transaction_nsu', '')
    slug = payload.get('slug') or payload.get('invoice_slug')
    if not (isinstance(nsu, str) and nsu.startswith('ZAVIA-') and nsu[6:].isdecimal()):
        return HttpResponse(status=400)
    if not (isinstance(transaction_nsu, str) and isinstance(slug, str)):
        return HttpResponse(status=400)
    if not (0 < len(transaction_nsu) <= 160 and 0 < len(slug) <= 160):
        return HttpResponse(status=400)
    try:
        confirmed = verify_and_apply(int(nsu[6:]), transaction_nsu, slug)
    except InfinitePayError:
        return HttpResponse(status=503)
    # 200 para eventos que não representam aprovação; nada é marcado pago sem confirmação.
    return HttpResponse(status=200)
