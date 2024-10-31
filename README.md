## README for Movies Reservation System API

This README provides detailed documentation for the Movies Reservation System API, outlining its functions, parameters, and how to use each API. The code leverages PostgreSQL for database management and supports functions for managing movies, customers, seats, and showtimes.

### Table of Contents
1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [API Functions](#api-functions)
    - [Database Connection](#database-connection)
    - [Table Creation](#table-creation)
    - [Customer Management](#customer-management)
    - [Movie Management](#movie-management)
    - [Seat Management](#seat-management)
    - [Utility Functions](#utility-functions)

---

### Getting Started

1. Install PostgreSQL and Python libraries:
    ```bash
    pip install psycopg2 werkzeug flask-login requests
    ```
2. Clone the repository and set up environment variables, including `DATABASE_URL`.

3. Execute the provided scripts for database setup, and start managing movie reservations, customers, and seat bookings.

---

### Configuration

1. **DATABASE_URL**: The database URL is set through an environment variable.
    - Format for local usage: `'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'`
  
---

### API Functions

#### 1. Database Connection

- **Function**: `start_connection()`
    - **Description**: Establishes a connection to the PostgreSQL database.
    - **Returns**: A database connection object if successful.
    - **Usage**:
      ```python
      conn = start_connection()
      ```

#### 2. Table Creation

- **Function**: `create_table(table_name, columns, conn)`
    - **Description**: Creates a database table.
    - **Parameters**:
      - `table_name` (str): Name of the table to create.
      - `columns` (str): Columns definition in SQL format.
      - `conn`: Database connection object.
    - **Usage**:
      ```python
      create_table('movie_table', movie_table_columns, conn)
      ```

- **Function**: `create_base_tables()`
    - **Description**: Creates base tables necessary for the reservation system.
    - **Usage**:
      ```python
      create_base_tables()
      ```

#### 3. Customer Management

- **Function**: `create_customer(username, password, email, conn)`
    - **Description**: Registers a new customer with hashed password storage.
    - **Parameters**:
      - `username` (str): Customer’s username.
      - `password` (str): Plain text password.
      - `email` (str): Customer’s email address.
      - `conn`: Database connection object.
    - **Usage**:
      ```python
      create_customer('john_doe', 'secure_password', 'john@example.com', conn)
      ```

- **Function**: `verify_user(username, hashed_password, conn)`
    - **Description**: Verifies the user’s login credentials.
    - **Parameters**:
      - `username` (str): Customer’s username.
      - `hashed_password` (str): Hashed password.
      - `conn`: Database connection object.
    - **Returns**: A dictionary with user information if credentials match, otherwise `None`.
    - **Usage**:
      ```python
      user = verify_user('john_doe', 'hashed_password', conn)
      ```

- **Function**: `get_user_by_username(username, conn)`
    - **Description**: Retrieves user data based on username.
    - **Parameters**:
      - `username` (str): Username to search.
      - `conn`: Database connection object.
    - **Returns**: User information or `None`.
    - **Usage**:
      ```python
      user = get_user_by_username('john_doe', conn)
      ```

#### 4. Movie Management

- **Function**: `fetch_movies()`
    - **Description**: Fetches popular movies from an external API.
    - **Returns**: List of dictionaries with movie details.
    - **Usage**:
      ```python
      movies = fetch_movies()
      ```

- **Function**: `update_movies_to_be_shown(conn)`
    - **Description**: Inserts movies from `fetch_movies()` into the database.
    - **Parameters**:
      - `conn`: Database connection object.
    - **Usage**:
      ```python
      update_movies_to_be_shown(conn)
      ```

#### 5. Seat Management

- **Function**: `populate_seats(conn)`
    - **Description**: Populates the `seats_table` with seat information.
    - **Parameters**:
      - `conn`: Database connection object.
    - **Usage**:
      ```python
      populate_seats(conn)
      ```

- **Function**: `reset_all_seats()`
    - **Description**: Resets all seats to available status.
    - **Usage**:
      ```python
      reset_all_seats()
      ```

- **Function**: `reset_specific_seat(seat_id)`
    - **Description**: Resets a specific seat based on `seat_id`.
    - **Parameters**:
      - `seat_id` (int): Seat ID to reset.
    - **Usage**:
      ```python
      reset_specific_seat(15)
      ```

- **Function**: `check_is_seat_available(seat_id)`
    - **Description**: Checks if a seat is available for booking.
    - **Parameters**:
      - `seat_id` (int): Seat ID to check.
    - **Returns**: `0` if available, `1` if booked, or a message if the seat doesn't exist.
    - **Usage**:
      ```python
      status = check_is_seat_available(15)
      ```

#### 6. Utility Functions

- **Function**: `parse_duration(duration_string)`
    - **Description**: Parses a movie duration string into total minutes.
    - **Parameters**:
      - `duration_string` (str): Duration string (e.g., "2 hours 30 minutes").
    - **Returns**: Total minutes as an integer.
    - **Usage**:
      ```python
      total_minutes = parse_duration("2 hours 30 minutes")
      ```

- **Function**: `set_movie_showTimes()`
    - **Description**: Calculates showtimes for each movie and populates the `movie_showTimes_table`.
    - **Usage**:
      ```python
      set_movie_showTimes()
      ```

- **Function**: `book_seat(seat_number, movie_id)`
    - **Description**: Books a seat for a specified movie.
    - **Parameters**:
      - `seat_number` (int): Seat number to book.
      - `movie_id` (int): ID of the movie for which the seat is being booked.
    - **Usage**:
      ```python
      book_seat(15, 1)
      ```