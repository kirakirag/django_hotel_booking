from django.test.client import Client
import pytest
from datetime import date, timedelta
from app.models import Booking, CustomUser

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
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room: Room = Room.objects.create(
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
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    # Create a room and an overlapping booking
    room: Room = Room.objects.create(
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
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room: Room = Room.objects.create(
        name="Room E", price_per_night=300.00, capacity=3)

    url = reverse('booking-list')
    data = {
        'room': room.id,
        'start_date': date.today() + timedelta(days=1),
        'end_date': date.today()
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = {
        'room': room.id,
        'start_date': date.today() - timedelta(1),
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
    assert len(response.data) == 2  # Expecting two rooms with capacity >=2
    assert response.data[0]['capacity'] == 2


@pytest.mark.django_db
def test_user_specific_booking_list():
    """
    Test that users see only their own bookings.
    """
    client = APIClient()

    # Create two users
    user1: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    user2: CustomUser = CustomUser.objects.create_user(
        email='testuser1@example.com', password='54321')

    # Create a room
    room: Room = Room.objects.create(
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
    assert len(response.data) == 1  # CustomUser1 should only see their booking
    assert response.data[0]['user'] == user1.id


@pytest.mark.django_db
def test_booking_overlap():
    """
    Test that a booking cannot be made if it overlaps with an existing booking.
    """
    client = APIClient()

    # Create a user and authenticate
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    # Create a room
    room: Room = Room.objects.create(
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


@pytest.mark.django_db
def test_cancel_booking():
    """
    Test cancellation of a booking.
    """
    client = APIClient()
    user = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    room: Room = Room.objects.create(
        name="Room K", price_per_night=200.00, capacity=2)
    booking: Booking = Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    url = reverse('booking-detail', args=[booking.booking_number]) + 'cancel/'
    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK
    booking.refresh_from_db()
    assert booking.status == 'cancelled'


@pytest.mark.django_db
def test_availability_after_cancellation(client: Client):
    """
    Test that a room becomes available after a booking is cancelled.
    """
    client = APIClient()
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='12345')
    client.force_authenticate(user=user)

    room: Room = Room.objects.create(
        name="Test Room", price_per_night=200.00, capacity=2)
    booking: Room = Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    # Cancel the booking
    cancel_url = reverse(
        'booking-detail', args=[booking.booking_number]) + 'cancel/'
    cancel_response = client.post(cancel_url)
    assert cancel_response.status_code == status.HTTP_200_OK

    # Try to rebook the same room for the same dates
    rebook_url = reverse('booking-list')
    rebook_data = {
        'room': room.id,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=1)
    }
    rebook_response = client.post(rebook_url, rebook_data)

    # The room should now be available, and the booking should succeed
    assert rebook_response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_user_registration():
    """
    Test user registration.
    """
    client = APIClient()
    url = reverse('register')
    data = {
        'email': 'testuser@example.com',
        'password': 'testpass123',
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"message": "User created successfully"}


@pytest.mark.django_db
def test_jwt_token_generation():
    """
    Test JWT token generation for a registered user.
    """
    client = APIClient()
    # First, register a new user
    client.post(reverse('register'), {
        'email': 'testuser@example.com',
        'password': 'jwtpass123',
    })

    # Now, obtain a JWT token for the registered user
    url = reverse('token_obtain_pair')
    response = client.post(
        url, {'email': 'testuser@example.com', 'password': 'jwtpass123'})

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_protected_endpoint_access():
    """
    Test that a protected endpoint requires a valid JWT token.
    """
    client = APIClient()
    # Attempt to access protected endpoint without a token
    response = client.get(reverse('protected'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Register and obtain a token
    client.post(reverse('register'), {
        'email': 'testuser@example.com',
        'password': 'securepass123',
    })
    token_response = client.post(reverse('token_obtain_pair'), {
                                 'email': 'testuser@example.com', 'password': 'securepass123'})
    token = token_response.data['access']

    # Attempt to access protected endpoint with the token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    protected_response = client.get(reverse('protected'))
    assert protected_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_user_can_view_their_bookings():
    client = APIClient()
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='viewpass')
    user1: CustomUser = CustomUser.objects.create_user(
        email='testuser1@example.com', password='viewpass')
    client.force_authenticate(user=user)

    room = Room.objects.create(
        name="View Room", price_per_night=100.00, capacity=2)

    booking: Booking = Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    Booking.objects.create(user=user1, room=room, start_date=date.today(
    ) + timedelta(2), end_date=date.today() + timedelta(days=3))

    url = reverse('booking-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['room_detail']['id'] == room.id
    assert response.data[0]['user'] == user.id
    assert response.data[0]['start_date'] == str(booking.start_date)
    assert response.data[0]['end_date'] == str(booking.end_date)


@pytest.mark.django_db
def test_user_can_cancel_booking():
    client = APIClient()
    user: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='cancelpass')
    client.force_authenticate(user=user)

    room: Room = Room.objects.create(
        name="Cancel Room", price_per_night=150.00, capacity=2)
    booking: Booking = Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    url = reverse('booking-detail', args=[booking.booking_number]) + 'cancel/'
    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK
    booking.refresh_from_db()
    assert booking.status == 'cancelled'


@pytest.mark.django_db
def test_user_cannot_cancel_others_booking():
    """
    Test that a user cannot cancel another user's booking.
    """
    client = APIClient()
    # Create two users
    user1: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='user1pass')
    user2: CustomUser = CustomUser.objects.create_user(
        email='testuser1@example.com', password='user2pass')

    # CustomUser1 creates a booking
    room: Room = Room.objects.create(
        name="Shared Room", price_per_night=200.00, capacity=3)
    booking: Booking = Booking.objects.create(user=user1, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    # CustomUser2 tries to cancel CustomUser1's booking
    client.force_authenticate(user=user2)
    cancel_url = reverse(
        'booking-detail', args=[booking.booking_number]) + 'cancel/'
    response = client.post(cancel_url)

    # CustomUser2 should receive a 403 Forbidden response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    client.force_authenticate(user=user1)
    response = client.post(cancel_url)

    # CustomUser1 should be able to cancel the booking
    assert response.status_code == status.HTTP_200_OK
    booking.refresh_from_db()
    assert booking.status == 'cancelled'


@pytest.mark.django_db
def test_superuser_can_view_all_bookings(client: Client):
    """
    Test that a superuser can view all bookings.
    """
    client = APIClient()
    superuser: CustomUser = CustomUser.objects.create_superuser(
        email='admin', password='admin')
    client.force_authenticate(user=superuser)

    user1: CustomUser = CustomUser.objects.create_user(
        email='testuser@example.com', password='user1pass')
    user2: CustomUser = CustomUser.objects.create_user(
        email='testuser1@example.com', password='user2pass')

    room: Room = Room.objects.create(
        name="Superuser Room", price_per_night=300.00, capacity=4)
    Booking.objects.create(user=user1, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))
    Booking.objects.create(user=user2, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=2))

    url = reverse('booking-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_superuser_can_cancel_any_booking(client: Client):
    """
    Test that a superuser can cancel any user's booking.
    """
    client = APIClient()
    superuser: CustomUser = CustomUser.objects.create_superuser(
        email='testuser@example.com', password='admin')
    client.force_authenticate(user=superuser)

    user: CustomUser = CustomUser.objects.create_user(
        email='testuser1@example.com', password='userpass')
    room: Room = Room.objects.create(
        name="Cancellable Room", price_per_night=200.00, capacity=2)
    booking: Booking = Booking.objects.create(user=user, room=room, start_date=date.today(
    ), end_date=date.today() + timedelta(days=1))

    cancel_url = reverse(
        'booking-detail', args=[booking.booking_number]) + 'cancel/'
    response = client.post(cancel_url)

    assert response.status_code == status.HTTP_200_OK
    booking.refresh_from_db()
    # Booking status should be updated to 'cancelled'
    assert booking.status == 'cancelled'


@pytest.mark.django_db
def test_create_booking_with_large_date():
    client = APIClient()
    user = CustomUser.objects.create_user(
        email='testuser@example.com', password='password')
    client.force_authenticate(user=user)
    room = Room.objects.create(
        name="Test Room", price_per_night=100, capacity=2)

    large_date = "9" * 10**6 + "-12-31"
    response = client.post(reverse('booking-list'), {
        'room': room.id,
        'start_date': large_date,
        'end_date': large_date
    })

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_booking_with_incorrect_date():
    client = APIClient()
    user = CustomUser.objects.create_user(
        email='testuser@example.com', password='password')
    client.force_authenticate(user=user)
    room = Room.objects.create(
        name="Test Room", price_per_night=100, capacity=2)

    incorrect_date = "date"
    response = client.post(reverse('booking-list'), {
        'room': room.id,
        'start_date': incorrect_date,
        'end_date': incorrect_date
    })

    assert response.status_code == 400


@pytest.mark.django_db
def test_room_list_normal():
    client = APIClient()
    url = reverse('room-list')

    # Create rooms
    Room.objects.create(name="Standard Room", price_per_night=100, capacity=2)
    Room.objects.create(name="Deluxe Room", price_per_night=200, capacity=3)

    # Testing with normal parameters
    response = client.get(
        url, {'min_price': 50, 'max_price': 100, 'capacity': 2})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_room_list_booked():
    client = APIClient()
    url = reverse('room-list')
    start_date = date.today().strftime("%Y-%m-%d")
    end_date = (date.today() + timedelta(1)).strftime("%Y-%m-%d")

    # Create user
    user = CustomUser.objects.create_user(
        email='testuser@example.com', password='password')

    # Create rooms
    room1 = Room.objects.create(
        name="Standard Room", price_per_night=100, capacity=2)
    room2 = Room.objects.create(
        name="Deluxe Room", price_per_night=200, capacity=3)

    # Book room
    Booking.objects.create(
        user=user,
        room=room1,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1)
    )

    response = client.get(
        url, {'min_price': 50, 'max_price': 250, 'capacity': 2, 'start_date': start_date, 'end_date': end_date})

    assert response.status_code == status.HTTP_200_OK
    # Only one room should match
    assert len(response.data) == 1

    # Book second room
    Booking.objects.create(
        user=user,
        room=room2,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1)
    )

    response = client.get(
        url, {'min_price': 50, 'max_price': 250, 'capacity': 2, 'start_date': start_date, 'end_date': end_date})

    assert response.status_code == status.HTTP_200_OK
    # No rooms should match
    assert len(response.data) == 0
