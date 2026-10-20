"""Admin ZÁVIA: gerenciamento seguro e claro para catálogo e pedidos."""
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html
from .photo_forms import ProductPhotoForm

from .infinitepay import release_abandoned_after_manual_confirmation
from .models import Category, Product, ProductVariant, ProductImage, Order, OrderItem, StoreInformation


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('active',)
    search_fields = ('name',)


class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'size', 'color', 'color_hex', 'stock', 'active')
    verbose_name_plural = 'Tamanhos e cores — estoque por SKU'


class ImageInline(admin.StackedInline):
    model = ProductImage
    form = ProductPhotoForm
    extra = 2
    fields = ('upload', 'preview', 'alt', 'position')
    readonly_fields = ('preview',)
    verbose_name_plural = 'Fotos reais — adicione quantas precisar (primeira posição vira a capa)'

    def preview(self, obj):
        if obj and obj.pk and obj.public_url:
            return format_html('<img src="{}" alt="Foto do produto" style="max-width:110px;max-height:130px;border-radius:8px">', obj.public_url)
        return 'Sem foto ainda'
    preview.short_description = 'Visualização'



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'effective_price_display', 'is_demo', 'active', 'featured', 'stock_quantity')
    list_filter = ('category', 'active', 'featured', 'is_demo')
    list_editable = ('active', 'featured')
    list_per_page = 30
    search_fields = ('name', 'slug', 'variants__sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline, ImageInline]
    actions = ('archive_selected', 'activate_real_products', 'remove_demos_safely')
    fieldsets = (
        ('Identificação', {'fields': ('category', 'name', 'slug', 'description')}),
        ('Preço e exposição', {'fields': ('price', 'sale_price', 'cost_price')}),
        ('Publicação', {'fields': ('active', 'featured', 'is_demo'),
                        'description': 'Cadastre fotos no fim da página, em GALERIA DE FOTOS. A menor posição é usada como capa. Publique quando estiver pronto.'}),
    )

    @admin.display(description='Preço de venda')
    def effective_price_display(self, obj):
        return f'R$ {obj.effective_price:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    @admin.display(description='Estoque')
    def stock_quantity(self, obj):
        return obj.stock_total

    @admin.action(description='Arquivar selecionados (sumir da vitrine, preservar pedidos)')
    def archive_selected(self, request, queryset):
        if not self.has_change_permission(request):
            self.message_user(request, 'Sem permissão para arquivar produtos.', messages.ERROR)
            return
        changed = queryset.update(active=False, featured=False)
        self.message_user(request, f'{changed} produto(s) arquivado(s). O histórico foi preservado.', messages.SUCCESS)

    @admin.action(description='Publicar selecionados que NÃO são fictícios')
    def activate_real_products(self, request, queryset):
        if not self.has_change_permission(request):
            self.message_user(request, 'Sem permissão.', messages.ERROR)
            return
        changed = queryset.filter(is_demo=False).update(active=True)
        self.message_user(request, f'{changed} produto(s) real(is) ativado(s). Confira fotos, preços e estoque.', messages.SUCCESS)

    @admin.action(description='Excluir fictícios selecionados (com confirmação)')
    def remove_demos_safely(self, request, queryset):
        if not self.has_delete_permission(request):
            self.message_user(request, 'Sem permissão para excluir produtos.', messages.ERROR)
            return
        candidates = queryset.filter(is_demo=True).order_by('pk')
        if request.POST.get('delete_demos_confirm') != 'EXCLUIR FICTICIOS':
            return TemplateResponse(request, 'admin/store/product/confirm_delete_demos.html', {
                **self.admin_site.each_context(request),
                'title': 'Exclusão cuidadosa de produtos fictícios',
                'products': candidates,
                'opts': self.model._meta,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'action_name': 'remove_demos_safely',
            })
        removed = candidates.count()
        candidates.delete()  # Pedidos históricos permanecem como snapshot, sem variação vinculada.
        self.message_user(request, f'{removed} produto(s) fictício(s) excluído(s) do cadastro, incluindo suas fotos.', messages.SUCCESS)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('variant', 'description', 'sku', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'total', 'stock_reserved', 'expired_reservation', 'created_at')
    list_filter = ('status', 'stock_reserved', 'created_at')
    actions = ['release_after_verified_unpaid']
    list_per_page = 30

    @admin.display(boolean=True, description='Reserva expirada')
    def expired_reservation(self, obj):
        return (obj.status == 'pending_payment' and obj.stock_reserved and
                obj.payment_expires_at is not None and obj.payment_expires_at <= timezone.now())

    @admin.action(description='Cancelar e repor estoque SOMENTE após conferir não pagamento na InfinitePay')
    def release_after_verified_unpaid(self, request, queryset):
        if not self.has_change_permission(request):
            self.message_user(request, 'Você não possui permissão.', level=messages.ERROR)
            return
        ids = list(queryset.values_list('pk', flat=True))
        if not ids or len(ids) > 10:
            self.message_user(request, 'Selecione de 1 a 10 pedidos.', level=messages.ERROR)
            return
        if request.POST.get('confirmed_unpaid') != 'CONFERI NA INFINITEPAY':
            return TemplateResponse(request, 'admin/store/order/confirm_release.html', {
                **self.admin_site.each_context(request),
                'title': 'Confirmação manual da InfinitePay — ação irreversível',
                'orders': queryset,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'action_name': 'release_after_verified_unpaid',
                'opts': self.model._meta,
            })
        count = 0
        for order_id in ids:
            try:
                if release_abandoned_after_manual_confirmation(order_id, staff_user=request.user, provider_checked=True):
                    count += 1
            except ValueError as exc:
                self.message_user(request, f'Pedido #{order_id}: {exc}', level=messages.WARNING)
        self.message_user(request, f'{count} reserva(s) devolvida(s) após conferência manual.', level=messages.INFO)

    search_fields = ('user__email', 'contact_email', 'gateway_payment_id')
    readonly_fields = ('user', 'created_at', 'total', 'shipping_amount', 'customer_name', 'contact_email', 'address', 'gateway_payment_id', 'gateway_preference_id', 'gateway_checkout_url', 'checkout_nonce', 'payment_status', 'stock_reserved', 'paid_at', 'payment_expires_at', 'status')
    inlines = [OrderItemInline]

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'size', 'color', 'stock', 'active')
    list_editable = ('stock', 'active')
    list_filter = ('size', 'color', 'active')
    search_fields = ('sku', 'product__name')


@admin.register(StoreInformation)
class StoreInformationAdmin(admin.ModelAdmin):
    """Uma configuração pública por loja. Nenhum token ou segredo aqui."""
    fieldsets = (
        ('Marca e identificação comercial', {'fields':('brand_name','legal_name','tax_id','business_address'),
            'description':'Preencha os dados reais da empresa antes de divulgar a loja. Não invente CNPJ ou endereço.'}),
        ('Atendimento', {'fields':('contact_email','contact_phone','service_hours','instagram_url','privacy_email'),
            'description':'WhatsApp no padrão internacional: 55 + DDD + número, sem espaços ou símbolos. Não coloque chaves de API.'}),
        ('Entregas e política de trocas', {'fields':('dispatch_region','shipping_preparation','delivery_estimate','shipping_details','exchange_details'),
            'description':'Informe prazos e procedimentos reais. Estes textos aparecem ao cliente na área de informações.'}),
    )
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not StoreInformation.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False
    def changelist_view(self, request, extra_context=None):
        existing=StoreInformation.objects.order_by('pk').first()
        if existing and self.has_view_or_change_permission(request, existing):
            from django.shortcuts import redirect
            return redirect('admin:store_storeinformation_change', existing.pk)
        return super().changelist_view(request, extra_context)
