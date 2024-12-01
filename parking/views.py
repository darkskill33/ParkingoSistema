from django.shortcuts import render, redirect, get_object_or_404
from .models import ParkingLocation, ParkingSpot, Reservation, Review
from .forms import UserReservationForm, ParkingSpotForm, ReviewForm
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings

def parking_spots_view(request):
    location_filter = request.GET.get('location_filter', 'Old Town Parking')  # Default to 'Old Town Parking'
    
    locations = ParkingLocation.objects.prefetch_related('spots').all()
    today = timezone.now().date()  # Get the current date

    # Apply location filter if it's not 'All Locations'
    if location_filter != 'All Locations':
        locations = locations.filter(name=location_filter)

    locations_with_approved_spots = []
    for location in locations:
        approved_spots = location.spots.filter(is_approved=True)
        if approved_spots.exists():
            for spot in approved_spots:
                spot.is_reserved = spot.reservations.filter(
                    start_time__lte=today, end_time__gte=today
                ).exists()
                spot.next_reservation = spot.reservations.filter(
                    start_time__gt=today
                ).order_by('start_time').first()
                spot.current_reservation = spot.reservations.filter(
                    start_time__lte=today, end_time__gte=today
                ).first()
            location.approved_spots = approved_spots
            locations_with_approved_spots.append(location)

    return render(
        request,
        'parking/parking_spots.html',
        {'locations': locations_with_approved_spots, 'today': today, 'location_filter': location_filter, 'all_locations': ParkingLocation.objects.all()}
    )


def reserve_parking_spot(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    today = timezone.now().date()
    latest_reservation = spot.reservations.filter(end_time__gte=today).order_by('start_time').first()

    if latest_reservation:
        spot_status = 'reserved'
        next_free_date = latest_reservation.end_time
    else:
        spot_status = 'available'
        next_free_date = None

    if request.method == 'POST':
        form = UserReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.spot = spot
            reservation.payment_due_time = timezone.now() + timedelta(minutes=5)

            if latest_reservation:
                if reservation.start_time <= latest_reservation.end_time and reservation.end_time > latest_reservation.start_time:
                    messages.error(
                        request, f"Spot {spot.spot_number} is reserved until {latest_reservation.end_time}."
                    )
                elif reservation.start_time < today:
                    messages.error(request, "Reservation start date cannot be in the past.")
                else:
                    reservation.save()
                    messages.success(
                        request,
                        f"Spot {spot.spot_number} reserved from {reservation.start_time} to {reservation.end_time}. Please pay within 5 minutes."
                    )
                    return redirect('profile')
            else:
                reservation.save()
                messages.success(
                    request,
                    f"Spot {spot.spot_number} reserved from {reservation.start_time} to {reservation.end_time}. Please pay within 5 minutes."
                )
                return redirect('profile')
        else:
            messages.error(request, "There was an issue with the reservation details. Please check your input.")
    else:
        form = UserReservationForm(initial={'start_time': today, 'user': request.user, 'spot': spot})

    return render(request, 'parking/reserve_spot_user.html', {
        'spot': spot,
        'form': form,
        'spot_status': spot_status,
        'next_free_date': next_free_date
    })
    
def unreserve_parking_spot(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.delete()  # Automatically frees the spot
    messages.success(request, "Your reservation has been canceled.")
    return redirect('profile')

def free_expired_spots():
    now = timezone.now()
    unpaid_reservations = Reservation.objects.filter(is_paid=False, payment_due_time__lte=now)

    for reservation in unpaid_reservations:
        if reservation.payment_due_time <= now:
            reservation.delete()


@login_required
def add_parking_spot(request):
    if request.method == 'POST':
        location_name = request.POST.get('new_location_name')  # Get the new location name if provided
        location_address = request.POST.get('new_location_address')  # Get the new location address if provided
        location_id = request.POST.get('location')  # Get the selected location id
        
        # If a new location is provided, create it
        if location_name:
            # Create a new location with the provided name and address
            location = ParkingLocation.objects.create(
                name=location_name,
                address=location_address  # Save the address if provided
            )
        else:
            # Else, get the existing location by id
            location = ParkingLocation.objects.get(id=location_id)
        
        # Now handle parking spot creation
        spot_number = request.POST['spot_number']
        daily_price = request.POST['daily_price']
        
        # Create the parking spot
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

    if reservation.spot.daily_price is None:
        messages.error(request, "This parking spot does not have a valid price set.")
        return redirect('profile')

    duration_in_days = (reservation.end_time - reservation.start_time).days + 1
    total_price = reservation.spot.daily_price * duration_in_days

    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f"Reservation for Spot {reservation.spot.spot_number}",
                    },
                    'unit_amount': int(total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/parking/success?reservation_id={reservation.id}',
            cancel_url='http://127.0.0.1:8000/parking/cancel',
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


def parking_location_profile(request, location_id):
    location = get_object_or_404(ParkingLocation, id=location_id)
    reviews = Review.objects.filter(location=location)  # Get all reviews for this location

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.location = location
            review.user = request.user
            review.save()
            return redirect('parking_location_profile', location_id=location.id)
    else:
        form = ReviewForm()

    return render(request, 'parking/parking_locations_profile.html', {
        'location': location,
        'form': form,
        'reviews': reviews,  # Pass reviews to the template
    })