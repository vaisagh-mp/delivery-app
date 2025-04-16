from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('delivery.urls')),  # Include the delivery app endpoints
]
