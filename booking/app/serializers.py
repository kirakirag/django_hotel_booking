from django.contrib.auth.models import User
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
        fields = ['booking_number', 'user', 'room',
                  'start_date', 'end_date', 'status']

    def to_representation(self, instance):
        """
        Convert `booking_number` to string in the response.
        """
        ret = super().to_representation(instance)
        ret['booking_number'] = str(instance.booking_number)
        return ret


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}
