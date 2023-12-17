from uuid import UUID
from datetime import date, datetime
# from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import viewsets, generics, status, views
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from .models import Booking, Room, CustomUser
from .serializers import RoomSerializer, BookingSerializer, UserSerializer
from .schema_serializers import (UserCreatedResponseSerializer,
                                 BookingCreateRequestSerializer,
                                 BookingCancelResponseSerializer,
                                 BookingFailedCreateResponseSerializer)


class BookingView(viewsets.ModelViewSet):
    """
    API view to create a new booking and list bookings of the authenticated user.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Booking:
        """
        Returns the booking the view is displaying.
        Override to use `booking_number` instead of primary key `id`.
        """
        queryset: QuerySet = self.get_queryset()
        filter_kwargs = {'booking_number': self.kwargs['pk']}
        # ensure pk is a valid UUID
        # try:
        #     uuid = UUID(self.kwargs['pk'])
        # except ValueError as exc:
        #     raise ValueError from exc

        # We return 404 if a user tries to access someone else's booking
        # to avoid revealing unnecessary info about the booking's existence
        # following the principle of least privilege here :)
        obj: Booking = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self) -> QuerySet:
        """Return only user's own bookings.

        Returns:
            QuerySet: user's bookings
        """
        if self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user, status="active")

    @extend_schema(
        request=BookingCreateRequestSerializer,
        responses={201: BookingSerializer,
                   400: BookingFailedCreateResponseSerializer},
        parameters=[
            OpenApiParameter(
                name="Authorization",
                description="Bearer Token for authorization",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER
            )
        ],
        examples=[
            OpenApiExample(
                "Create Booking Example",
                summary="Example of a booking creation request",
                value={
                    "room": 1,
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-03"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Unsuccessful Create Booking Example",
                summary="Booking failed",
                value={
                    "error": "Room is not available for the selected dates."
                },
                response_only=True,
                status_codes=[400]
            )
        ]
    )
    def create(self, request, *args, **kwargs) -> Response:
        """
        Create a booking if the room is available.
        """
        serializer: BookingSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the room_id directly from the request data
        room_id: str = request.data.get('room')
        start_date: date = serializer.validated_data.get('start_date')
        end_date: date = serializer.validated_data.get('end_date')

        try:
            room: Room = Room.objects.get(pk=room_id)
        except Exception:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        if room.is_available(start_date, end_date) and start_date < end_date and start_date >= date.today():
            serializer.save(user=self.request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({"error": "Room is not available for the selected dates."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: BookingCancelResponseSerializer,
            404: OpenApiTypes.OBJECT
        },
        parameters=[],
        examples=[
            OpenApiExample(
                'Booking Cancelled Example',
                summary='Booking successfully cancelled',
                response_only=True,
                status_codes=['200'],
                value={'status': 'booking cancelled'}
            ),
            OpenApiExample(
                'Booking Cancel Unauthorized Example',
                summary='Unauthorized cancellation attempt or booking does not exist',
                response_only=True,
                status_codes=['404'],
                value={'status': 'Not Found'}
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request: Request, pk=None) -> Response:
        """
        Cancel a booking.
        """
        booking: Booking = self.get_object()
        if request.user == booking.user or request.user.is_superuser:
            booking.status = 'cancelled'
            booking.save()
            return Response({'status': 'booking cancelled'}, status=status.HTTP_200_OK)

        return Response({'status': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)


class RoomListView(generics.ListAPIView):
    """
    API view to list and filter rooms based on price, capacity, and availability.
    """
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter("min_price", OpenApiTypes.FLOAT,
                             OpenApiParameter.QUERY),
            OpenApiParameter("max_price", OpenApiTypes.FLOAT,
                             OpenApiParameter.QUERY),
            OpenApiParameter("capacity", OpenApiTypes.INT,
                             OpenApiParameter.QUERY),
            OpenApiParameter("start_date", OpenApiTypes.DATE,
                             OpenApiParameter.QUERY),
            OpenApiParameter("end_date", OpenApiTypes.DATE,
                             OpenApiParameter.QUERY)
        ],
        responses={200: RoomSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """Return a QuerySet of filtered rooms.

        Returns:
            QuerySet: rooms filtered as requested
        """
        queryset: QuerySet = Room.objects.all()
        min_price: float = self.request.query_params.get('min_price')
        max_price: float = self.request.query_params.get('max_price')
        desired_capacity: int = self.request.query_params.get('capacity')
        start_date_str: str = self.request.query_params.get('start_date')
        end_date_str: str = self.request.query_params.get('end_date')

        if min_price is not None:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price_per_night__lte=max_price)
        if desired_capacity is not None:
            queryset = queryset.filter(capacity__gte=desired_capacity)

        try:
            start_date = datetime.strptime(
                start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(
                end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            return queryset

        if start_date and end_date:
            queryset = [room for room in queryset if room.is_available(
                start_date, end_date)]
        return queryset


class CreateUserView(views.APIView):
    """
    A view that handles user sign-up.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @extend_schema(
        request=UserSerializer,
        responses={
            201: UserCreatedResponseSerializer,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'User Created Example',
                summary='User created successfully',
                response_only=True,
                status_codes=['201'],
                value={'message': 'User created successfully'}
            ), OpenApiExample(
                'User Not Created Example',
                summary='User was not created',
                response_only=True,
                status_codes=['400'],
                value={'message': 'custom user with this email already exists'}
            )
        ]
    )
    def post(self, request: Request) -> Response:
        """Register a new user.

        Args:
            request (Request): new user data 

        Returns:
            Response: HTTP status 201 if successful, status 400 otherwise
        """
        serializer: UserSerializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            CustomUser.objects.create_user(**serializer.validated_data)
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# TODO clean up test views


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You have access to the protected view!"})
