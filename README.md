# Hotel Booking API

This project is a hotel booking API built with Django and Django REST Framework (DRF). It provides endpoints for users to create, view, and cancel bookings, as well as manage rooms.

## Features

- User registration and authentication.
- Room listing with the ability to filter by price, capacity, and availability.
- Booking creation and cancellation.
- Admin functionalities to add, edit, and delete rooms and bookings.
- Secure endpoints with JWT authentication.
- Auto-generated API documentation with `drf-spectacular`.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:

- Python 3.11
- pip (Python package installer)

### Installation

1. Clone the repository:

```
git clone https://github.com/kirakirag/django_hotel_booking.git
cd hotel-booking-api
```

2. Launch the app in Docker:
```
docker-compose build && docker-compose up
```

3. Create a superuser account:
```
docker-compose run web python booking/manage.py createsuperuser
```

4. (Optional) Use my [simple Vue front-end](https://github.com/kirakirag/vue_hotel_booking) to interact with the app

## Testing

This app uses automatic testing with pytest. To view and modify the tests:
Go to ```booking/tests```

To run tests:
```docker-compose run web pytest booking```

## API Documentation

To view the auto-generated API documentation:
- Open http://localhost:8000/api/schema/ for the raw schema.
- To access the interactive documentation, open http://localhost:8000/api/docs/ for Swagger UI

## Usage
This app exposes the following endpoints:

- /api/token/: POST request to authenticate users and retrieve a JWT token.
- /api/token/refresh/: POST request to refresh an expired JWT token.
- /app/bookings/: POST requests for booking creation.
- /app/bookings/{id}/: POST requests to manage an existing booking.
- /app/rooms/: GET request for room search and availability checks.
- /app/register/: POST request for user registration.