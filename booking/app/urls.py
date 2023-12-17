from django.urls import path
from .views import RoomListView, BookingView

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('bookings/', BookingView.as_view(), name='booking-list')
]
