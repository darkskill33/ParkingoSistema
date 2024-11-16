from django.shortcuts import render, redirect, get_object_or_404
from .models import ParkingLocation, ParkingSpot, Reservation
from .forms import ReservationForm, UserReservationForm
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone  # Correct import for timezone.now

def parking_spots_view(request):
    locations = ParkingLocation.objects.prefetch_related('spots').all()
    return render(request, 'parking/parking_spots.html', {'locations': locations})

def reserve_parking_spot(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    
    if spot.is_reserved:
        messages.error(request, "This spot is already reserved.")
        return redirect('parking_spots')
    
    if request.method == 'POST':
        form = UserReservationForm(request.POST)
        if form.is_valid():
            start_time = form.cleaned_data['start_time']
            duration_in_days = form.cleaned_data['duration_in_days']
            end_time = form.cleaned_data['end_time']  # The form calculates this
            
            # Create the reservation
            Reservation.objects.create(
                user=request.user,
                spot=spot,
                duration_in_days=duration_in_days,
                start_time=start_time,
                end_time=end_time
            )
            
            # Mark the spot as reserved
            spot.is_reserved = True
            spot.save()
            
            messages.success(request, f"Spot {spot.spot_number} reserved from {start_time} to {end_time}!")
            return redirect('profile')  # Redirect to profile after reservation
        
    else:
        # Now correctly use timezone.now() to set the initial start time
        form = UserReservationForm(initial={'start_time': timezone.now()})
    
    return render(request, 'parking/reserve_spot_user.html', {'spot': spot, 'form': form})

def unreserve_parking_spot(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    spot = reservation.spot
    spot.is_reserved = False
    spot.save()
    reservation.delete()
    messages.success(request, "Your reservation has been canceled and the spot is now available.")
    return redirect('profile')  # Redirect to profile or wherever you want after unreserving
