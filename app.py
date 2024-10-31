from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import psycopg2
from functools import wraps
import os
from database.db import start_connection,book,check_overlaps,reset_specific_seat,fetch_movies,update_movies_to_be_shown,set_movie_showTimes,clear_movies_table
conn=start_connection()
app = Flask(__name__)

# Database connection
DATABASE_URL = 'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except psycopg2.Error as e:
            return jsonify({'error': 'Database error', 'message': str(e)}), 500
        except Exception as e:
            return jsonify({'error': 'Server error', 'message': str(e)}), 500
    return wrapper

# User Management Endpoints
@app.route('/api/users/register', methods=['POST'])
@handle_errors
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if username exists
            cur.execute("SELECT * FROM registred_customers_table WHERE customer_username = %s", (username,))
            if cur.fetchone():
                return jsonify({'error': 'Username already exists'}), 409
                
            hashed_password = generate_password_hash(password)
            cur.execute("""
                INSERT INTO registred_customers_table (customer_username, customer_password, customer_email)
                VALUES (%s, %s, %s) RETURNING customer_id
            """, (username, hashed_password, email))
            customer_id = cur.fetchone()[0]
            conn.commit()
            
    return jsonify({'message': 'User registered successfully', 'customer_id': customer_id}), 201

@app.route('/api/users/login', methods=['POST'])
@handle_errors
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'error': 'Missing credentials'}), 400
        
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT customer_id, customer_password 
                FROM registred_customers_table 
                WHERE customer_username = %s
            """, (username,))
            result = cur.fetchone()
            
            if not result or not check_password_hash(result[1], password):
                return jsonify({'error': 'Invalid credentials'}), 401
                
    return jsonify({'message': 'Login successful', 'customer_id': result[0]}), 200

@app.route('/api/users/<username>', methods=['GET'])
@handle_errors
def get_user(username):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT customer_id, customer_username, customer_email 
                FROM registred_customers_table 
                WHERE customer_username = %s
            """, (username,))
            user = cur.fetchone()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            return jsonify({
                'customer_id': user[0],
                'username': user[1],
                'email': user[2]
            })

# Movie Endpoints
@app.route('/api/movies', methods=['GET'])
@handle_errors
def get_movies():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT movie_id, movie_name, movie_duration, 
                       start_time, end_time, available_seats, 
                       start_times, movie_poster, release_year 
                FROM movie_table
            """)
            movies = cur.fetchall()
            
            return jsonify([{
                'movie_id': m[0],
                'name': m[1],
                'duration': m[2],
                'start_time': m[3].strftime('%H:%M') if m[3] else None,
                'end_time': m[4].strftime('%H:%M') if m[4] else None,
                'available_seats': m[5],
                'start_times': [t.strftime('%Y-%m-%d %H:%M') for t in m[6]] if m[6] else [],
                'poster': m[7],
                'release_year': m[8]
            } for m in movies])

@app.route('/api/movies/update', methods=['POST'])
@handle_errors
def update_movies():
    clear_movies_table(conn)
    update_movies_to_be_shown(conn)
    set_movie_showTimes()
  
    return jsonify({'message': 'Movies updated successfully'})

@app.route('/api/movies/showtimes', methods=['GET'])
@handle_errors
def get_showtimes():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT movie_id, movie_name, start_times 
                FROM movie_table 
                WHERE start_times IS NOT NULL
            """)
            showtimes = cur.fetchall()
            
            return jsonify([{
                'movie_id': s[0],
                'movie_name': s[1],
                'showtimes': [t.strftime('%Y-%m-%d %H:%M') for t in s[2]] if s[2] else []
            } for s in showtimes])

# Seat Endpoints
@app.route('/api/seats', methods=['GET'])
@handle_errors
def get_seats():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM seats_table")
            seats = cur.fetchall()
            
            return jsonify([{
                'seat_id': s[0],
                'category': s[1],
                'price': float(s[2]),
                'is_in_use': s[5],
                'is_corner': s[6],
                'has_headphones': s[7],
                'has_cupholder': s[8]
            } for s in seats])

@app.route('/api/seats/<int:seat_id>', methods=['GET'])
@handle_errors
def get_seat(seat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM seats_table WHERE seat_id = %s", (seat_id,))
            seat = cur.fetchone()
            
            if not seat:
                return jsonify({'error': 'Seat not found'}), 404
                
            return jsonify({
                'seat_id': seat[0],
                'category': seat[1],
                'price': float(seat[2]),
                'is_in_use': seat[5],
                'is_corner': seat[6],
                'has_headphones': seat[7],
                'has_cupholder': seat[8]
            })

@app.route('/api/seats/reset', methods=['POST'])
@handle_errors
def reset_seats():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE seats_table 
                SET seat_is_in_use = FALSE, 
                    seat_free_time = CURRENT_TIMESTAMP,
                    movie_id = NULL
            """)
            conn.commit()
            
    return jsonify({'message': 'All seats reset successfully'})

@app.route('/api/seats/reset/<int:seat_id>', methods=['POST'])
@handle_errors
def reset_seat(seat_id):
    reset_specific_seat(seat_id)
            
    return jsonify({'message': f'Seat {seat_id} reset successfully'})

@app.route('/api/seats/check/<int:seat_id>', methods=['GET'])
@handle_errors
def check_seat(seat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT seat_is_in_use FROM seats_table WHERE seat_id = %s", (seat_id,))
            result = cur.fetchone()
            
            if not result:
                return jsonify({'error': 'Seat does not exist'}), 404
                
            return jsonify({
                'seat_id': seat_id,
                'is_available': not result[0]
            })

# Booking Endpoints
@app.route('/api/bookings', methods=['POST'])
@handle_errors
def create_booking():
    data = request.get_json()
    seat_id = data.get('seat_id')
    movie_id = data.get('movie_id')
    customer_id = data.get('customer_id')
    if not all([seat_id, movie_id, customer_id]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    booking_id=book(seat_id,movie_id,customer_id)
    return jsonify({
        'message': 'Booking created successfully',
        'booking_id': booking_id
    }), 201

@app.route('/api/bookings/customer/<int:customer_id>', methods=['GET'])
@handle_errors
def get_customer_bookings(customer_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.booking_id, b.seat_id, b.movie_id, 
                       b.booking_start_time, b.booking_end_time,
                       m.movie_name, s.seat_category, s.seat_price
                FROM bookings_table b
                JOIN movie_table m ON b.movie_id = m.movie_id
                JOIN seats_table s ON b.seat_id = s.seat_id
                WHERE b.customer_id = %s AND b.is_confirmed = TRUE
                ORDER BY b.booking_start_time DESC
            """, (customer_id,))
            bookings = cur.fetchall()
            
            return jsonify([{
                'booking_id': b[0],
                'seat_id': b[1],
                'movie_id': b[2],
                'start_time': b[3].strftime('%Y-%m-%d %H:%M'),
                'end_time': b[4].strftime('%Y-%m-%d %H:%M'),
                'movie_name': b[5],
                'seat_category': b[6],
                'price': float(b[7])
            } for b in bookings])

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@handle_errors
def cancel_booking(booking_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get seat_id before deleting booking
            cur.execute("SELECT seat_id FROM bookings_table WHERE booking_id = %s", (booking_id,))
            result = cur.fetchone()
            
            if not result:
                return jsonify({'error': 'Booking not found'}), 404
                
            seat_id = result[0]
            
            # Delete booking
            cur.execute("DELETE FROM bookings_table WHERE booking_id = %s", (booking_id,))
            
            # Reset seat status
            cur.execute("""
                UPDATE seats_table 
                SET seat_is_in_use = FALSE, 
                    movie_id = NULL 
                WHERE seat_id = %s
            """, (seat_id,))
            
            conn.commit()
            
    return jsonify({'message': 'Booking cancelled successfully'})

# Payment Endpoints
@app.route('/api/payments/price/<int:seat_id>', methods=['GET'])
@handle_errors
def get_seat_price(seat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT seat_price FROM seats_table WHERE seat_id = %s", (seat_id,))
            result = cur.fetchone()
            
            if not result:
                return jsonify({'error': 'Seat not found'}), 404
                
            return jsonify({
                'seat_id': seat_id,
                'price': float(result[0])
            })

@app.route('/api/payments', methods=['POST'])
@handle_errors
def process_payment():
    data = request.get_json()
    customer_id = data.get('customer_id')
    amount = data.get('amount')
    booking_id = data.get('booking_id')
    
    if not all([customer_id, amount, booking_id]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Here you would typically integrate with a payment processor
    # For now, we'll just mark the booking as confirmed
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE bookings_table 
                SET is_confirmed = TRUE 
                WHERE booking_id = %s AND customer_id = %s
                RETURNING booking_id
            """, (booking_id, customer_id))
            
            if cur.rowcount == 0:
                return jsonify({'error': 'Invalid booking or customer'}), 404
                
            conn.commit()
            
    return jsonify({
        'message': 'Payment processed successfully',
        'booking_id': booking_id,
        'amount': amount
    })

if __name__ == '__main__':
    app.run(debug=True)