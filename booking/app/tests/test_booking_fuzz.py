import pytest
import uuid
from datetime import timedelta
from hypothesis import given, settings, strategies as st
from django.urls import reverse
from rest_framework.test import APIClient
from app.models import CustomUser, Room


@pytest.mark.django_db
class TestBookingAPIFuzz:

    @given(
        start_date=st.dates(),
        end_date=st.dates(),
        room_id=st.integers()
    )
    @settings(max_examples=50, deadline=timedelta(milliseconds=1000))
    def test_create_booking_fuzz(self, start_date, end_date, room_id):
        # Setup a test user and authenticate
        user = CustomUser.objects.create_user(
            email=f'{uuid.uuid4()}@example.com', password='123')
        client = APIClient()
        client.force_authenticate(user=user)

        # Create a test room (or you can use a real room ID if you have room fixtures)
        room = Room.objects.create(
            name=f'{uuid.uuid4()}', price_per_night=100, capacity=2)

        # Form the data payload with hypothesis-generated data
        data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'room': room.id if room_id > 0 else room_id  # Using real room ID or fuzzed ID
        }

        # Make the API request
        response = client.post(reverse('booking-list'), data)

        # Check response -- adjust according to your API's logic
        assert response.status_code in [201, 400]
