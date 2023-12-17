from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Booking, Room
from .serializers import RoomSerializer, BookingSerializer


class BookingView(viewsets.ModelViewSet):
    """
    API view to create a new booking and list bookings of the authenticated user.
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a booking if the room is available.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room_id = serializer.validated_data.get('room').id
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        room = Room.objects.get(pk=room_id)

        if room.is_available(start_date, end_date) and start_date < end_date:
            serializer.save(user=self.request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"error": "Room is not available for the selected dates."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        """
        booking = self.get_object()
        if request.user == booking.user or request.user.is_superuser:
            booking.status = 'cancelled'
            booking.save()
            return Response({'status': 'booking cancelled'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unauthorized'}, status=status.HTTP_403_FORBIDDEN)


class RoomListView(generics.ListAPIView):
    """
    API view to list and filter rooms based on price and capacity.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Room.objects.all()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        capacity = self.request.query_params.get('capacity')

        if min_price is not None:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price_per_night__lte=max_price)
        if capacity is not None:
            queryset = queryset.filter(capacity=capacity)

        return queryset
