from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BookingView, RoomListView, CreateUserView, ProtectedView

router = SimpleRouter()
# router.register(r'bookings', BookingView, basename='booking')

# Manually add routes for desired actions
booking_list = BookingView.as_view({
    'get': 'list',
    'post': 'create'
})
booking_detail = BookingView.as_view({
    'get': 'retrieve',
    # 'put': 'update',  # Remove or comment out methods you don't want
    # 'patch': 'partial_update',  # Remove or comment out methods you don't want
    # 'delete': 'destroy',  # Remove or comment out methods you don't want
})
booking_cancel = BookingView.as_view({
    'post': 'cancel'
})

urlpatterns = [
    path('bookings/', booking_list, name='booking-list'),
    path('bookings/<uuid:pk>/', booking_detail, name='booking-detail'),
    path('bookings/<uuid:pk>/cancel/', booking_cancel, name='booking-cancel'),
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('register/', CreateUserView.as_view(), name='register'),
    # TODO clean up test views
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),
]
