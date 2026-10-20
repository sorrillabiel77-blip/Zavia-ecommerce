from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from decimal import Decimal
from .models import Category, Product, ProductVariant

class StoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category=Category.objects.create(name='Leggings',slug='leggings')
        cls.product=Product.objects.create(category=category,name='Legging Teste',slug='legging-teste',price=Decimal('149.90'),image_url='/static/img/legging-cacau.webp')
        cls.variant=ProductVariant.objects.create(product=cls.product,sku='TEST-M',size='M',color='Mocha',stock=5)

    def test_home_and_detail(self):
        self.assertContains(self.client.get(reverse('home')),'Legging Teste')
        self.assertContains(self.client.get(reverse('product_detail',args=['legging-teste'])),'Legging Teste')

    def test_cart_has_real_price_and_persists_through_login(self):
        result=self.client.post(reverse('cart_add'),{'variant_id':self.variant.pk,'quantity':2})
        self.assertEqual(result.status_code,302)
        self.assertContains(self.client.get(reverse('cart')),'299,80')
        user=User.objects.create_user(username='teste',password='SuaSenhaBemLonga!82')
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse('cart')),'Legging Teste')

    def test_out_of_stock_rejected(self):
        self.client.post(reverse('cart_add'),{'variant_id':self.variant.pk,'quantity':6})
        self.assertContains(self.client.get(reverse('cart')),'esperando você')

    def test_invalid_cart_quantity_rejected(self):
        result=self.client.post(reverse('cart_add'),{'variant_id':self.variant.pk,'quantity':0})
        self.assertEqual(result.status_code,400)

    def test_checkout_requires_login(self):
        self.assertEqual(self.client.get(reverse('checkout')).status_code, 302)

    def test_dashboard_requires_staff(self):
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,302)
        user=User.objects.create_user(username='admin',password='UmaSenhaBemForte!83',is_staff=True)
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse('dashboard')),'Gestão da')

    def test_health(self):
        self.assertEqual(self.client.get(reverse('health')).content,b'ok')


from unittest.mock import patch
import json
from .models import Order
from .infinitepay import InfinitePayError, cents

class CheckoutInfinitePayTests(StoreTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.buyer=User.objects.create_user(username='clientezavia',email='cliente@example.com',password='SenhaSeguraZavia!23')

    def add_cart(self):
        self.client.force_login(self.buyer)
        self.client.post(reverse('cart_add'), {'variant_id':self.variant.pk,'quantity':'1'})

    def valid_form(self):
        self.client.get(reverse('checkout'))
        return {'nonce':self.client.session['zavia_checkout_nonce'],
                'full_name':'Cliente de Teste','email':'cliente@example.com',
                'phone':'11998887777','postal_code':'01001000','street':'Rua de Teste',
                'number':'12','neighborhood':'Centro','city':'São Paulo','state':'SP'}

    def create_order(self):
        self.add_cart()
        with patch('store.views.create_payment_link',return_value=('ZAVIA-1','https://checkout.infinitepay.com.br/fake')):
            self.client.post(reverse('checkout'), self.valid_form())
        return Order.objects.get(user=self.buyer)

    @override_settings(ZAVIA_CHECKOUT_ENABLED=True,INFINITEPAY_API_KEY='inchk_fake',INFINITEPAY_TAG='minha-loja',ZAVIA_SHIPPING_FLAT='12.00')
    def test_pending_and_reservation(self):
        order=self.create_order()
        self.assertEqual(order.total,Decimal('161.90'))
        self.assertEqual(order.status,'pending_payment')
        self.assertEqual(order.gateway_preference_id,'ZAVIA-1')
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock,4)

    @override_settings(ZAVIA_CHECKOUT_ENABLED=True,INFINITEPAY_API_KEY='inchk_fake',INFINITEPAY_TAG='minha-loja',ZAVIA_SHIPPING_FLAT='12.00')
    def test_return_requires_authenticated_confirmation(self):
        order=self.create_order()
        self.client.get(reverse('payment_return',args=[order.pk])+'?paid=true')
        order.refresh_from_db()
        self.assertEqual(order.status,'pending_payment')
        query=f'?order_nsu=ZAVIA-{order.pk}&slug=slug123&transaction_nsu=tx123'
        with patch('store.infinitepay.payment_check',return_value={'success':True,'paid':True,'amount':16190}):
            self.client.get(reverse('payment_return',args=[order.pk])+query)
        order.refresh_from_db()
        self.assertEqual(order.status,'paid')
        with patch('store.infinitepay.payment_check',return_value={'success':True,'paid':True,'amount':16190}):
            self.client.get(reverse('payment_return',args=[order.pk])+query)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock,4)

    @override_settings(ZAVIA_CHECKOUT_ENABLED=True,INFINITEPAY_API_KEY='inchk_fake',INFINITEPAY_TAG='minha-loja',ZAVIA_SHIPPING_FLAT='12.00')
    def test_webhook_rechecks_amount(self):
        order=self.create_order()
        body={'order_nsu':f'ZAVIA-{order.pk}','invoice_slug':'slug123','transaction_nsu':'tx123'}
        with patch('store.infinitepay.payment_check',return_value={'success':True,'paid':True,'amount':100}):
            self.client.post(reverse('payment_webhook'),json.dumps(body),content_type='application/json')
        order.refresh_from_db()
        self.assertEqual(order.status,'pending_payment')
        with patch('store.infinitepay.payment_check',return_value={'success':True,'paid':True,'amount':16190}):
            self.client.post(reverse('payment_webhook'),json.dumps(body),content_type='application/json')
        order.refresh_from_db()
        self.assertEqual(order.status,'paid')

    @override_settings(ZAVIA_CHECKOUT_ENABLED=True,INFINITEPAY_API_KEY='inchk_fake',INFINITEPAY_TAG='minha-loja',ZAVIA_SHIPPING_FLAT='12.00')
    def test_demo_cannot_checkout(self):
        self.add_cart()
        self.product.is_demo=True
        self.product.save(update_fields=['is_demo'])
        self.client.post(reverse('checkout'),self.valid_form())
        self.assertFalse(Order.objects.filter(user=self.buyer).exists())

    @override_settings(ZAVIA_CHECKOUT_ENABLED=True,INFINITEPAY_API_KEY='inchk_fake',INFINITEPAY_TAG='minha-loja',ZAVIA_SHIPPING_FLAT='12.00')
    def test_failed_link_releases_stock(self):
        self.add_cart()
        with patch('store.views.create_payment_link',side_effect=InfinitePayError('simulada')):
            self.client.post(reverse('checkout'),self.valid_form())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock,5)
        self.assertEqual(Order.objects.get(user=self.buyer).status,'cancelled')

    def test_cents(self):
        self.assertEqual(cents(Decimal('149.90')),14990)
