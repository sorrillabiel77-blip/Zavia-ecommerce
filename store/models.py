from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

class Category(models.Model):
    name = models.CharField('Nome', max_length=90, unique=True)
    slug = models.SlugField('Identificador', unique=True)
    active = models.BooleanField('Ativa', default=True)
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
    def __str__(self): return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Categoria')
    name = models.CharField('Nome', max_length=160)
    slug = models.SlugField('Identificador', unique=True)
    description = models.TextField('Descrição', blank=True)
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    sale_price = models.DecimalField('Preço promocional', max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    cost_price = models.DecimalField('Custo', max_digits=10, decimal_places=2, default=0)
    image_url = models.CharField('Imagem principal (URL/estático)', max_length=500, default='/static/img/conjunto-mocha.webp')
    featured = models.BooleanField('Destaque', default=False)
    active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-featured','-created_at']
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('product_detail', args=[self.slug])
    @property
    def effective_price(self):
        return self.sale_price if self.sale_price is not None and self.sale_price < self.price else self.price
    @property
    def stock_total(self):
        return sum(v.stock for v in self.variants.all())

class ProductVariant(models.Model):
    SIZES = [('PP','PP'),('P','P'),('M','M'),('G','G'),('GG','GG'),('XG','XG'),('UN','Único')]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='Produto')
    sku = models.CharField('SKU', max_length=60, unique=True)
    size = models.CharField('Tamanho', max_length=3, choices=SIZES)
    color = models.CharField('Cor', max_length=70)
    color_hex = models.CharField('Cor hexadecimal', max_length=7, default='#B9938E')
    stock = models.PositiveIntegerField('Estoque', default=0)
    active = models.BooleanField('Ativo', default=True)
    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
        constraints = [models.UniqueConstraint(fields=['product','size','color'],name='zavia_unique_product_size_color')]
        ordering = ['color','size']
    def __str__(self): return f'{self.product.name} / {self.color} / {self.size}'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name='Produto')
    image_url = models.CharField('URL da imagem', max_length=500)
    alt = models.CharField('Texto alternativo', max_length=140, blank=True)
    position = models.PositiveSmallIntegerField('Posição', default=0)
    class Meta:
        verbose_name = 'Imagem de produto'
        verbose_name_plural = 'Imagens de produtos'
        ordering = ['position','id']
    def __str__(self): return self.alt or self.image_url[:45]

class Order(models.Model):
    STATUSES = [('pending_payment','Aguardando pagamento'),('paid','Pago'),('preparing','Separação'),('shipped','Enviado'),('delivered','Entregue'),('cancelled','Cancelado'),('refunded','Estornado')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=24, choices=STATUSES, default='pending_payment')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    address = models.TextField(blank=True)
    gateway_payment_id = models.CharField(max_length=140, blank=True)
    notes = models.TextField(blank=True)
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
    def __str__(self): return f'Pedido #{self.pk}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    description = models.CharField(max_length=220)
    sku = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'
    def __str__(self): return self.description
