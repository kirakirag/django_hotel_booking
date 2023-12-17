from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Room, Booking, CustomUser


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
    Serializer for the CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Use create_user method to handle password hashing
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Update user info, handling password hashing if password is provided
        password = validated_data.pop('password', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance
