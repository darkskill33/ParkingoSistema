from django.contrib import admin
from .models import ParkingLocation, ParkingSpot, Reservation
from .forms import ReservationForm

@admin.register(ParkingLocation)
class ParkingLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('spot_number', 'location', 'is_reserved')
    list_filter = ('is_reserved', 'location')
    search_fields = ('spot_number', 'location__name')


# admin.py
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'spot', 'start_time', 'end_time', 'duration_in_days')
    search_fields = ('user__username', 'spot__spot_number')
    
    # Ensure the user is automatically set if not provided by the admin
    def save_model(self, request, obj, form, change):
        if not obj.user:  # If no user is set, set it to the currently logged-in admin
            obj.user = request.user
        super().save_model(request, obj, form, change)
