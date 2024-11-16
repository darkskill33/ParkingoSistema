# parkingosistema/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', user_views.login_view, name='login'),  
    path('users/', include('users.urls')), 
    path('parking/', include('parking.urls')),
]
