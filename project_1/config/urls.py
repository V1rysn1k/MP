from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),        # Все URL из catalog/urls.py будут доступны без префикса
    path('schedule/', include('schedule.urls')),  # Все URL из schedule/urls.py будут с префиксом schedule/
]

handler404 = 'catalog.views.not_found_page'