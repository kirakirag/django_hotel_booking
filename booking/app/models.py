import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import date


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
        """
        Check if the room is available for booking between start_date and end_date.
        Only considers active bookings.
        """
        overlapping_bookings = Booking.objects.filter(
            room=self,
            status="active",
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        return not overlapping_bookings.exists()


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email: str = self.normalize_email(email)
        user: CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class that uses email as the primary identifier
    """
    email: models.EmailField = models.EmailField('email address', unique=True)
    is_staff: models.BooleanField = models.BooleanField(default=False)
    is_active: models.BooleanField = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Booking(models.Model):
    """
    Represents a booking of a room by a user.

    Attributes:
        user (ForeignKey): A reference to the User who made the booking.
        room (ForeignKey): The Room that is booked.
        start_date (DateField): The start date of the booking.
        end_date (DateField): The end date of the booking.
        status (CharField): Status of the booking: active or cancelled.
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled")
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active")
    booking_number = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    user: CustomUser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room: Room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date: date = models.DateField()
    end_date: date = models.DateField()
