from rest_framework import serializers
from .models import Room, Booking


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for the Room model.
    """

    class Meta:
        model = Room
        fields = ['id', 'name', 'price_per_night', 'capacity']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'room', 'start_date', 'end_date']
