from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingView, RoomListView, CreateUserView, ProtectedView

router = DefaultRouter()
router.register(r'bookings', BookingView, basename='booking')

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('register/', CreateUserView.as_view(), name='register'),
    # TODO clean up test views
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),
]
