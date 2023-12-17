from rest_framework import serializers


class BookingCancelResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class UserCreatedResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class BookingCreateRequestSerializer(serializers.Serializer):
    room = serializers.IntegerField(help_text="ID of the room to be booked")
    start_date = serializers.DateField(help_text="Start date of the booking")
    end_date = serializers.DateField(help_text="End date of the booking")


class BookingFailedCreateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
