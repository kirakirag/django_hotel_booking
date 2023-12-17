from django.contrib import admin
from app.models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_night', 'capacity')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'user', 'room',
                    'start_date', 'end_date', 'status')
    search_fields = ('booking_number', 'user__username', 'room__name')
    list_filter = ('status',)
    readonly_fields = ('booking_number',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'room')
        return self.readonly_fields
