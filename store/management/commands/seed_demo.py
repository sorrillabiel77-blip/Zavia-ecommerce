from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import Category, Product, ProductVariant

PRODUCTS = [
    ('Conjuntos','conjuntos','Conjunto Aura Mocha','conjunto-aura-mocha','Conforto e elegância para o treino e além.', '249.90','conjunto-mocha.webp','Mocha','#876757'),
    ('Tops','tops','Top Essential Areia','top-essential-areia','Sustentação suave com design atemporal.','99.90','top-areia.webp','Areia','#DCC3AA'),
    ('Leggings','leggings','Legging Sculpt Nude','legging-sculpt-nude','Cintura alta, conforto e movimento.','159.90','legging-nude.webp','Nude','#D1BBA8'),
    ('Shorts','shorts','Short Move Rosé','short-move-rose','Leveza e liberdade em cada movimento.','119.90','short-rose.webp','Rosé','#BE8B91'),
    ('Leggings','leggings','Legging Performance Cacau','legging-performance-cacau','Tecido macio para dias intensos.','169.90','legging-cacau.webp','Cacau','#624036'),
    ('Conjuntos','conjuntos','Conjunto Flow Rosé','conjunto-flow-rose','Para quem vive o movimento com estilo.','239.90','conjunto-rose.webp','Rosé','#C18B83'),
]
class Command(BaseCommand):
    help = 'Cria produtos DEMONSTRATIVOS sem apagar nem alterar produtos existentes'
    @transaction.atomic
    def handle(self,*args,**kwargs):
        created_count=0
        for cat_name,cat_slug,name,slug,desc,price,img,color,hexcolor in PRODUCTS:
            cat,_=Category.objects.get_or_create(slug=cat_slug,defaults={'name':cat_name})
            product,created=Product.objects.get_or_create(slug=slug,defaults={
                'category':cat,'name':name,'description':desc,'price':Decimal(price),
                'image_url':'/static/img/'+img,'featured':True,
            })
            if created:
                created_count+=1
                for size in ['P','M','G','GG']:
                    ProductVariant.objects.create(product=product,sku=f'ZV-{slug.upper()[:16]}-{size}',size=size,color=color,color_hex=hexcolor,stock=8)
        self.stdout.write(self.style.SUCCESS(f'Demo: {created_count} novos produtos; nenhuma edição em produtos existentes.'))
