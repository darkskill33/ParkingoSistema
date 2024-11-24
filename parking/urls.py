# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('parking-spots/', views.parking_spots_view, name='parking_spots'),
    path('reserve-spot/<int:spot_id>/', views.reserve_parking_spot, name='reserve_parking_spot'),
    path('unreserve-spot/<int:reservation_id>/', views.unreserve_parking_spot, name='unreserve_parking_spot'),
    path('add-spot/', views.add_parking_spot, name='add_parking_spot'),
    path('checkout/<int:reservation_id>/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
]
