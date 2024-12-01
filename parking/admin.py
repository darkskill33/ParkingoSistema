from django.contrib import admin
from .models import ParkingLocation, ParkingSpot, Reservation

@admin.register(ParkingLocation)
class ParkingLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')  # Add latitude and longitude here if you want them displayed in the list
    search_fields = ('name', 'address')
    fields = ('name', 'address', 'latitude', 'longitude')  # Include latitude and longitude in the form
    ordering = ('name',)
    
    
@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('spot_number', 'location', 'is_approved')
    list_filter = ('is_reserved', 'location', 'is_approved')
    search_fields = ('spot_number', 'location__name')
    actions = ['approve_spots']

    def approve_spots(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected spots have been approved.")
    approve_spots.short_description = "Approve selected spots"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'spot', 'start_time', 'end_time', 'get_duration')
    search_fields = ('user__username', 'spot__spot_number')

    def get_duration(self, obj):
        """Display the duration of the reservation in days."""
        return obj.duration  # Calls the `duration` property in the model
    get_duration.short_description = 'Duration (days)'  # Label for the admin column

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)
