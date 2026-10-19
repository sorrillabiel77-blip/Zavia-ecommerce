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

    def test_checkout_is_disabled(self):
        self.assertContains(self.client.get(reverse('checkout')),'não é possível pagar')

    def test_dashboard_requires_staff(self):
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,302)
        user=User.objects.create_user(username='admin',password='UmaSenhaBemForte!83',is_staff=True)
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse('dashboard')),'Gestão da')

    def test_health(self):
        self.assertEqual(self.client.get(reverse('health')).content,b'ok')
