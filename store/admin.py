from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','active','slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('active',)

class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku','size','color','color_hex','stock','active')

class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image_url','alt','position')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','price','sale_price','active','featured','stock_quantity')
    list_filter = ('category','active','featured')
    search_fields = ('name','slug','variants__sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline,ImageInline]
    list_editable = ('active','featured')
    def stock_quantity(self, obj): return obj.stock_total
    stock_quantity.short_description = 'Estoque'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('variant','description','sku','quantity','unit_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','status','total','created_at')
    list_filter = ('status','created_at')
    search_fields = ('user__email','contact_email','gateway_payment_id')
    readonly_fields = ('user','created_at','total','shipping_amount','customer_name','contact_email','address','gateway_payment_id')
    inlines = [OrderItemInline]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku','product','size','color','stock','active')
    list_editable = ('stock','active')
    list_filter = ('size','color','active')
    search_fields = ('sku','product__name')
