import uuid
from django.db import models
from datetime import date
from django.contrib.auth.models import User, AbstractUser


class Room(models.Model):
    """
    Represents a room that can be booked.

    Attributes:
        name (CharField): The name of the room.
        price_per_night (DecimalField): The price per night for booking the room.
        capacity (IntegerField): The maximum number of people the room can accommodate.
    """
    name: str = models.CharField(max_length=100)
    price_per_night: float = models.DecimalField(
        max_digits=6, decimal_places=2)
    capacity: int = models.IntegerField()

    def is_available(self, start_date: date, end_date: date) -> bool:
        overlapping_bookings = Booking.objects.filter(
            room=self,
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        return not overlapping_bookings.exists()


class Booking(models.Model):
    """
    Represents a booking of a room by a user.

    Attributes:
        user (ForeignKey): A reference to the User who made the booking.
        room (ForeignKey): The Room that is booked.
        start_date (DateField): The start date of the booking.
        end_date (DateField): The end date of the booking.
    """
    booking_number = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
    room: Room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date: date = models.DateField()
    end_date: date = models.DateField()


# TODO use email as username
# class CustomUser(AbstractUser):
#     username = None
#     email = models.EmailField(
#         'email address', unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.email
