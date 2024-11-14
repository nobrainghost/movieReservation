# Movie Reservation System Documentation

A python and PostgreSQL-based movie theater reservation system that handles movie listings, seat management, bookings, and payments.
https://roadmap.sh/projects/movie-reservation-system

## Table of Contents
- [Database Configuration](#database-configuration)
- [Core Functions](#core-functions)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)

## Database Configuration

```python
DATABASE_URL = 'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'
```

### Connection Management
- `start_connection()`: Establishes database connection using configured credentials
- `create_table(table_name, columns, conn)`: Creates database tables with specified schema

## Core Functions

### User Management

#### `create_customer(username, password, email, conn)`
Creates a new customer account with hashed password.

```python
# Example usage
create_customer('johndoe', 'password123', 'john@example.com', conn)
```

#### `verify_user(username, hashed_password, conn)` 
Verifies user credentials and returns user data if valid.

```python
# Example usage
user_data = verify_user('johndoe', 'hashed_password', conn)
```

#### `get_user_by_username(username, conn)`
Retrieves user details by username.

```python
# Example usage
user = get_user_by_username('johndoe', conn)
```

### Movie Management

#### `fetch_movies()`
Fetches trending movies from IMDB API.
- Returns: List of movies with title, duration, poster URL, and release year

#### `update_movies_to_be_shown(conn)`
Updates database with fetched movies.

#### `set_movie_showTimes()`
Automatically generates show times for all movies:
- Operational hours: 8:00 AM - 11:58 PM
- Includes 30-minute breaks between shows
- Handles duration parsing and scheduling

### Seat Management

#### `populate_seats(conn)`
Initializes theater seats with:
- Front seats (20): $40-50
- Middle seats (60): $25-40
- Back seats (20): $12-25
- Various amenities (headphones, cupholders, corner positions)

#### `reset_all_seats()`
Resets all seats to available status.

#### `reset_specific_seat(seat_id)`
Resets a specific seat to available status.

#### `check_is_seat_available(seat_id)`
Checks seat availability:
- Returns 0: Available
- Returns 1: Booked
- Returns "seat does not exist": Invalid seat

### Booking Management

#### `check_overlaps(seat_id, start_time, end_time)`
Checks for booking time conflicts.

#### `book(seat_id, movie_id, customer_id)`
Creates a new booking:
- Validates seat availability
- Checks time conflicts
- Creates booking record
- Returns confirmation or error message

#### `get_bookings_by_customer(customer_id)`
Retrieves all bookings for a specific customer.

#### `delete_booking(booking_id)`
Cancels a specific booking.

### Payment Processing

#### `get_price(seat_id)`
Retrieves price for specific seat.

#### `make_payment(customer_id, amount, booking_id)`
Processes payment and confirms booking.

## API Endpoints

### User Management
```
POST /api/users/register
{
    "username": string,
    "password": string,
    "email": string
}

POST /api/users/login
{
    "username": string,
    "password": string
}

GET /api/users/{username}
```

### Movies
```
GET /api/movies
Returns list of available movies

POST /api/movies/update
Updates movie database with latest trending movies

GET /api/movies/showtimes
Returns all movie showtimes
```

### Seats
```
GET /api/seats
Returns all seats with status

GET /api/seats/{seat_id}
Returns specific seat details

POST /api/seats/reset
Resets all seats to available

POST /api/seats/reset/{seat_id}
Resets specific seat to available

GET /api/seats/check/{seat_id}
Checks seat availability
```

### Bookings
```
POST /api/bookings
{
    "seat_id": integer,
    "movie_id": integer,
    "customer_id": integer
}

GET /api/bookings/customer/{customer_id}
Returns all bookings for customer

DELETE /api/bookings/{booking_id}
Cancels specific booking
```

### Payments
```
GET /api/payments/price/{seat_id}
Returns price for specific seat

POST /api/payments
{
    "customer_id": integer,
    "amount": float,
    "booking_id": integer
}
```

## Database Schema

### movie_table
```sql
CREATE TABLE movie_table (
    movie_id SERIAL PRIMARY KEY,
    movie_name VARCHAR(256),
    movie_duration VARCHAR(50) NOT NULL,
    start_time TIME,
    end_time TIME,
    available_seats INTEGER[],
    start_times TIMESTAMP[],
    movie_poster VARCHAR(256),
    release_year INTEGER
);
```

### seats_table
```sql
CREATE TABLE seats_table (
    seat_id SERIAL PRIMARY KEY,
    seat_category VARCHAR(20) CHECK(seat_category IN ('Front','Middle','Backseat')),
    seat_price DECIMAL(10,2),
    seat_book_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seat_free_time TIMESTAMP,
    seat_is_in_use BOOLEAN DEFAULT TRUE,
    seat_is_corner BOOLEAN DEFAULT FALSE,
    seat_has_headphones BOOLEAN DEFAULT FALSE,
    seat_has_cupholder BOOLEAN DEFAULT FALSE,
    movie_id INTEGER REFERENCES movie_table(movie_id) ON DELETE CASCADE
);
```

### bookings_table
```sql
CREATE TABLE bookings_table (
    booking_id SERIAL PRIMARY KEY,
    seat_id INTEGER REFERENCES seats_table(seat_id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movie_table(movie_id) ON DELETE CASCADE,
    booking_start_time TIMESTAMP,
    booking_end_time TIMESTAMP,
    is_confirmed BOOLEAN DEFAULT TRUE,
    customer_id INTEGER REFERENCES registred_customers_table(customer_id) ON DELETE CASCADE
);
```

### registred_customers_table
```sql
CREATE TABLE registred_customers_table (
    customer_id SERIAL PRIMARY KEY,
    customer_username VARCHAR(255),
    customer_password VARCHAR(255),
    customer_email VARCHAR(255)
);
```

## Error Handling
- All functions include appropriate error handling
- Database connection errors are caught and logged
- Invalid seat/movie IDs return appropriate error messages
- Booking conflicts are properly handled and reported

## Dependencies
- psycopg2: PostgreSQL adapter for Python
- werkzeug.security: Password hashing
- requests: API calls for movie data
- datetime: Time and date handling

## Installation
1. Set up PostgreSQL database
2. Configure DATABASE_URL
3. Run table creation scripts
4. Initialize seats with `populate_seats()`
5. Fetch initial movies with `update_movies_to_be_shown()`
6. Set up show times with `set_movie_showTimes()`
