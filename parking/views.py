from django.shortcuts import render, redirect, get_object_or_404
from .models import ParkingLocation, ParkingSpot, Reservation
from .forms import UserReservationForm, ParkingSpotForm
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings

def parking_spots_view(request):
    locations = ParkingLocation.objects.prefetch_related('spots').all()
    approved_spots = ParkingSpot.objects.filter(is_approved=True)
    
    now = timezone.now()  # Get the current time

    # Add the current reservation status for each spot in locations
    for location in locations:
        for spot in location.spots.all():
            spot.is_reserved = spot.reservations.filter(start_time__lte=now, end_time__gte=now).exists()
            spot.next_reservation = spot.reservations.filter(start_time__gt=now).order_by('start_time').first()
            spot.current_reservation = spot.reservations.filter(start_time__lte=now, end_time__gte=now).first()

    return render(request, 'parking/parking_spots.html', {'locations': locations, 'approved_spots': approved_spots, 'now': now})


def reserve_parking_spot(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    
    current_time = timezone.now()
    latest_reservation = spot.reservations.filter(end_time__gte=current_time).order_by('start_time').first()

    # If the spot is currently reserved, calculate when it will be free
    if latest_reservation:
        spot_status = 'reserved'
        next_free_time = latest_reservation.end_time
    else:
        spot_status = 'available'
        next_free_time = None

    if request.method == 'POST':
        form = UserReservationForm(request.POST)
        
        if form.is_valid():
            # Now that form is valid, just save it and pass the data to create a reservation
            reservation = form.save(commit=False)
            reservation.user = request.user  # Set the logged-in user (or pass user explicitly in the form)
            reservation.spot = spot  # Assign the spot (if not prefilled)
            reservation.save()  # Save the reservation object
            messages.success(request, f"Spot {spot.spot_number} reserved from {reservation.start_time} to {reservation.end_time}.")
            return redirect('profile')  # Or wherever you'd like to redirect after success
        else:
            # Print out the form errors to debug
            print(form.errors)  # Log or print form errors to debug
            messages.error(request, "There was an issue with the reservation details. Please check your input.")
            print(request.POST)

    else:
        # Pre-fill the form with the current user and spot
        form = UserReservationForm(initial={'start_time': timezone.now(), 'user': request.user, 'spot': spot})

    return render(request, 'parking/reserve_spot_user.html', {
        'spot': spot,
        'form': form,
        'spot_status': spot_status,
        'next_free_time': next_free_time
    })


def unreserve_parking_spot(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.delete()  # Automatically frees the spot
    messages.success(request, "Your reservation has been canceled.")
    return redirect('profile')

def free_expired_spots():
    """Periodic task to free expired spots."""
    for spot in ParkingSpot.objects.all():
        spot.release_if_expired()


@login_required
def add_parking_spot(request):
    if request.method == 'POST':
        # Handle form submission
        location_name = request.POST.get('new_location_name')  # Get the new location name if provided
        location_id = request.POST.get('location')  # Get the selected location id
        
        # If a new location is provided, create it
        if location_name:
            location = ParkingLocation.objects.create(name=location_name)
        else:
            # Else, get the existing location by id
            location = ParkingLocation.objects.get(id=location_id)
        
        # Now handle parking spot creation
        spot_number = request.POST['spot_number']
        daily_price = request.POST['daily_price']
        
        spot = ParkingSpot.objects.create(
            location=location,
            spot_number=spot_number,
            daily_price=daily_price,
            is_approved=False  # By default, the spot will not be approved
        )
        
        # Redirect to parking spots page after adding
        return redirect('parking_spots')

    else:
        # Handle GET request
        locations = ParkingLocation.objects.all()
        return render(request, 'parking/add_parking_spot.html', {'locations': locations})


@login_required
def checkout(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Ensure that the spot has a valid daily_price
    if reservation.spot.daily_price is None:
        messages.error(request, "This parking spot does not have a valid price set.")
        return redirect('profile')  # Redirect to profile if price is not set

    # Calculate the duration in days
    duration = reservation.end_time - reservation.start_time
    duration_in_days = duration.days  # Get the number of full days

    # Calculate the total price: spot's daily price * number of days
    total_price = reservation.spot.daily_price * duration_in_days

    if request.method == 'POST':
        # Create a payment intent with the calculated total_price
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Change to EUR or any currency you need
                    'product_data': {
                        'name': f"Reservation for Spot {reservation.spot.spot_number}",
                    },
                    'unit_amount': int(total_price * 100),  # Stripe expects the amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/parking/success?reservation_id={reservation.id}',  # Full URL
            cancel_url='http://127.0.0.1:8000/parking/cancel',  # Full URL
        )
        return redirect(session.url, code=303)

    return render(request, 'parking/checkout.html', {'reservation': reservation, 'total_price': total_price})


def success(request):
    reservation_id = request.GET.get('reservation_id')  # Get reservation_id from query parameter
    if reservation_id:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        reservation.is_paid = True
        reservation.save()  # Mark reservation as paid
        messages.success(request, f"Payment for Spot {reservation.spot.spot_number} was successful!")
    
    return render(request, 'parking/success.html')


def cancel(request):
    return render(request, 'parking/cancel.html')


