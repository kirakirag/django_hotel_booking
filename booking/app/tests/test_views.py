import pytest
from django.contrib.auth.models import User
from datetime import date, timedelta
from app.models import Booking

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Room


@pytest.mark.django_db
def test_room_list():
    """
    Test listing of rooms.
    """
    client = APIClient()

    # Create sample rooms
    Room.objects.create(name="Room A", price_per_night=100.00, capacity=2)
    Room.objects.create(name="Room B", price_per_night=150.00, capacity=3)

    url = reverse('room-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_create_booking():
    """
    Test creation of a booking.
    """
    client = APIClient()

    # Create a user and authenticate
    user = User.objects.create_user(username='testuser', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room = Room.objects.create(
        name="Room C", price_per_night=200.00, capacity=4)

    url = reverse('booking-list')
    data = {
        'room': room.id,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=1)
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED, response.data


@pytest.mark.django_db
def test_room_unavailability():
    """
    Test booking a room that is not available.
    """
    client = APIClient()

    # Create a user and authenticate
    user = User.objects.create_user(
        username='unavailable_testuser', password='12345')
    client.force_authenticate(user=user)

    # Create a room and an overlapping booking
    room = Room.objects.create(
        name="Room D", price_per_night=250.00, capacity=2)
    Booking.objects.create(
        user=user,
        room=room,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1)
    )

    # Attempt to create an overlapping booking
    url = reverse('booking-list')
    data = {
        'room': room.id,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=1)
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_invalid_date_range():
    """
    Test booking with an end date before the start date.
    """
    client = APIClient()

    # Create a user and authenticate
    user = User.objects.create_user(username='date_testuser', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room = Room.objects.create(
        name="Room E", price_per_night=300.00, capacity=3)

    url = reverse('booking-list')
    data = {
        'room': room.id,
        'start_date': date.today() + timedelta(days=1),
        'end_date': date.today()
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_room_filtering():
    """
    Test filtering rooms by capacity.
    """
    client = APIClient()

    # Create sample rooms with different capacities
    Room.objects.create(name="Room F", price_per_night=100.00, capacity=1)
    Room.objects.create(name="Room G", price_per_night=200.00, capacity=2)
    Room.objects.create(name="Room H", price_per_night=300.00, capacity=3)

    url = reverse('room-list') + '?capacity=2'
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # Expecting only one room with capacity 2
    assert response.data[0]['capacity'] == 2


@pytest.mark.django_db
def test_user_specific_booking_list():
    """
    Test that users see only their own bookings.
    """
    client = APIClient()

    # Create two users
    user1 = User.objects.create_user(username='user1', password='12345')
    user2 = User.objects.create_user(username='user2', password='54321')

    # Create a room
    room = Room.objects.create(
        name="Room I", price_per_night=150.00, capacity=2)

    # Create bookings for each user
    Booking.objects.create(user=user1, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))
    Booking.objects.create(user=user2, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=2))

    # Authenticate as user1 and get bookings
    client.force_authenticate(user=user1)
    url = reverse('booking-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # User1 should see only their booking
    assert response.data[0]['user'] == user1.id


@pytest.mark.django_db
def test_booking_overlap():
    """
    Test that a booking cannot be made if it overlaps with an existing booking.
    """
    client = APIClient()

    # Create a user and authenticate
    user = User.objects.create_user(
        username='overlap_testuser', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room = Room.objects.create(
        name="Room J", price_per_night=150.00, capacity=2)

    # Create an initial booking
    Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    # Attempt to create an overlapping booking
    url = reverse('booking-list')
    data = {
        'room': room.id,
        'start_date': date.today(),  # Overlaps with the existing booking
        'end_date': date.today() + timedelta(days=10)
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
