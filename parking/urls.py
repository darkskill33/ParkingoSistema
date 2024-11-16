# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('parking-spots/', views.parking_spots_view, name='parking_spots'),
    path('reserve-spot/<int:spot_id>/', views.reserve_parking_spot, name='reserve_parking_spot'),
    path('unreserve-spot/<int:reservation_id>/', views.unreserve_parking_spot, name='unreserve_parking_spot'),
]
