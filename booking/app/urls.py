from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingView, RoomListView

router = DefaultRouter()
router.register(r'bookings', BookingView, basename='booking')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # ... other url patterns ...
    path('rooms/', RoomListView.as_view(), name='room-list'),  # Room list view
    path('', include(router.urls)),  # Includes all URLs from the router
]
