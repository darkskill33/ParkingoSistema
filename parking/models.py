from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link reservation to a user
    spot = models.ForeignKey('ParkingSpot', on_delete=models.CASCADE)  # Use a string reference here
    duration_in_days = models.PositiveIntegerField()  # Duration of the reservation in days
    start_time = models.DateTimeField()  # When reservation starts
    end_time = models.DateTimeField()  # When reservation ends

    def __str__(self):
        return f"Reservation for {self.user.username} at spot {self.spot.spot_number} from {self.start_time} to {self.end_time}"
    
    def delete(self, *args, **kwargs):
        # Set the parking spot's is_reserved to False before deleting the reservation
        self.spot.is_reserved = False
        self.spot.save()
        super().delete(*args, **kwargs)

class ParkingLocation(models.Model):
    name = models.CharField(max_length=100)  # Name of the parking location (e.g., "Main Street Garage")
    address = models.CharField(max_length=200, blank=True)  # Optional address

    def __str__(self):
        return self.name

class ParkingSpot(models.Model):
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE, related_name="spots")
    spot_number = models.CharField(max_length=10)  # Spot identifier (e.g., "A1", "B2")
    is_reserved = models.BooleanField(default=False)  # Whether the spot is reserved

    def reserve(self, user, start_time, end_time):
        """Reserve this parking spot."""
        if not self.is_reserved:
            reservation = Reservation.objects.create(
                user=user,
                spot=self,
                start_time=start_time,
                end_time=end_time
            )
            self.is_reserved = True
            self.save()
            return reservation
        return None

    def release(self):
        """Release this parking spot."""
        self.is_reserved = False
        self.save()

    def __str__(self):
        return f"Spot {self.spot_number} at {self.location.name}"
