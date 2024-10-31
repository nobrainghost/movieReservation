from flask import Flask, session, request, jsonify
from database.db import (
    create_customer,
    start_connection,
    get_user_by_username,
    verify_user,
    get_booking_by_id,
    delete_booking,
    process_payment,
    book_seat,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'jhsdvhfvajhbf231354354'

"""USER AUTHENTICATION BELOW"""
@app.route("/api/signup", methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    conn = start_connection()
    
    # Validate if user exists
    create_customer(username, password, email, conn)
    return jsonify({"message": "Registration Successful"}), 201


@app.route("/api/signin", methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    conn = start_connection()
    
    user = get_user_by_username(username, conn)
    if user is not None:
        customer_id, customer_name, hashed_password = user
        if check_password_hash(hashed_password, password):
            session['customer_id'] = customer_id
            session['customer_name'] = customer_name
            return jsonify({"message": "Login Successful"}), 200
        else:
            return jsonify({"error": "Invalid Credentials"}), 401
    else:
        return jsonify({"error": "User not Found"}), 404


@app.route("/api/signout", methods=['GET'])
def logout():
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    return jsonify({"message": "Successful logout"}), 200


@app.route("/api/verify-user", methods=['POST'])
def verify_user_endpoint():
    data = request.json
    username = data['username']
    conn = start_connection()
    
    if verify_user(username, conn):
        return jsonify({"message": "User exists"}), 200
    else:
        return jsonify({"error": "User does not exist"}), 404


"""BOOKING API BELOW"""
@app.route("/api/booking/<int:booking_id>", methods=['GET'])
def get_booking(booking_id):
    conn = start_connection()
    booking = get_booking_by_id(booking_id, conn)
    if booking:
        return jsonify({"booking": booking}), 200
    else:
        return jsonify({"error": "Booking not found"}), 404


@app.route("/api/booking/<int:booking_id>", methods=['DELETE'])
def delete_booking_endpoint(booking_id):
    conn = start_connection()
    success = delete_booking(booking_id, conn)
    if success:
        return jsonify({"message": "Booking deleted successfully"}), 204
    else:
        return jsonify({"error": "Booking not found"}), 404


@app.route("/api/pay", methods=['POST'])
def process_payment_endpoint():
    data = request.json
    booking_id = data['booking_id']
    payment_info = data['payment_info']
    
    # Assume process_payment handles the payment processing logic
    success = process_payment(booking_id, payment_info)
    if success:
        return jsonify({"message": "Payment processed successfully"}), 200
    else:
        return jsonify({"error": "Error processing payment"}), 400


if __name__ == "__main__":
    app.run(debug=True)
