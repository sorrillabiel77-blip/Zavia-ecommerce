from django.contrib import admin
from django.urls import include, path
from store import views

admin.site.site_header = 'ZÁVIA • Administração'
admin.site.site_title = 'ZÁVIA Admin'
admin.site.index_title = 'Gestão da loja'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('conta/', include('django.contrib.auth.urls')),
    path('', include('store.urls')),
]
