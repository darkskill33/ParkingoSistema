from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Reservation

class ReservationForm(forms.ModelForm):
    # Custom fields to pre-populate or set specific initial values can be defined here
    start_time = forms.DateTimeField(initial=timezone.now)  # Set current time as default for start_time
    end_time = forms.DateTimeField(initial=timezone.now() + timezone.timedelta(days=1))  # End time is 1 day after start

    class Meta:
        model = Reservation  # Bind this form to the Reservation model
        fields = ['user', 'spot', 'duration_in_days', 'start_time', 'end_time']


class UserReservationForm(forms.Form):
    start_time = forms.DateTimeField(initial=timezone.now, label="Start Date")
    duration_in_days = forms.IntegerField(min_value=1, label="Reservation Duration (days)")
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        duration_in_days = cleaned_data.get('duration_in_days')
        
        if start_time and duration_in_days:
            # Calculate the end time based on the duration
            end_time = start_time + timedelta(days=duration_in_days)
            cleaned_data['end_time'] = end_time
        
        return cleaned_data
