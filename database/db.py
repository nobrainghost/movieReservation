
import psycopg2
from psycopg2 import sql,Error

import os

class Config:
    ##below credentials are local and therefore not a security risk
    DATABASE_URL=os.environ.get('DATABASE_URL') or 'dbname=moviesreservation user=beamer password=allhailkingjulien host=localhost'

def start_connection():
    try:
        conn=psycopg2.connect(Config.DATABASE_URL)
        print("Connection Successful")
        return conn
    except Exception as e:
        print(f"Error Attempting Connection: {e}")

def create_table(table_name,columns,conn):
    """
    Creates a table, taking in:
        table_name: for table Name,
        columns: a string containing table columns 
        conn: database connection
    """

    create_table_query_gen=f"""
    CREATE TABLE IF NOT EXISTS {table_name}({columns});

    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_query_gen)
    

    conn.commit()
    print(f"Table {table_name} Created Succefully")


seat_table_columns="""
seat_id SERIAL PRIMARY KEY,

seat_category VARCHAR(20) CHECK(seat_category IN ('Front','Middle','Backseat')),
seat_price DECIMAL(10,2),
seat_book_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
seat_free_time  TIMESTAMP,
seat_is_in_use BOOLEAN DEFAULT TRUE,
seat_is_corner BOOLEAN DEFAULT FALSE,
seat_has_headphones BOOLEAN DEFAULT FALSE,
seat_has_cupholder BOOLEAN DEFAULT FALSE,
movie_id INTEGER REFERENCES movie_table(movie_id) ON DELETE CASCADE

"""

movie_table_columns="""
movie_id INTEGER PRIMARY KEY,
movie_name VARCHAR(256),
movie_duration INTEGER NOT NULL,
start_time TIME,
end_time TIME,
available_seats INTEGER[],
start_times TIMESTAMP[]

"""

customer_table_columns="""
customer_id INTEGER REFERENCES registred_customers_table(customer_id) ON DELETE CASCADE,
customer_name VARCHAR(100),
customer_booked_seat INTEGER REFERENCES seats_table(seat_id) ON DELETE CASCADE,
customer_email VARCHAR(50),
customer_payment_method VARCHAR(50),
is_couple BOOLEAN DEFAULT FALSE

"""
registred_customers_columns="""
customer_id SERIAL PRIMARY KEY,
customer_username VARCHAR(255),
customer_password VARCHAR(255),
customer_email VARCHAR(255)
"""

# def create_base_tables():
#     conn=start_connection()
#     create_table('movie_table',movie_table_columns,conn)
#     create_table('seats_table',seat_table_columns,conn)
#     create_table('registred_customers_table',registred_customers_columns,conn)
#     create_table('customer_table',customer_table_columns,conn)

# create_base_tables()

##move these to a separate file and import the commands
#basic functions
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin


def create_customer(username,password,email,conn):
    hashed_password=generate_password_hash(password,method='pbkdf2:sha256')
    cursor=conn.cursor()
    query=sql.SQL("INSERT INTO registred_customers_table (customer_username,customer_password,customer_email) VALUES (%s,%s,%s)")
    cursor.execute(query,[username,hashed_password,email])
    conn.commit()

# conn=start_connection()
# create_customer('benar','allhailkingjulien','bean@gmail.com',conn)

def verify_user(username,hashed_password,conn):
    try:
        cursor=conn.cursor()

        query='''SELECT customer_id,customer_username,email FROM registred_customers_table WHERE customer_username=? AND password = ?'''
        cursor.execute(query,(username,hashed_password))
        user=cursor.fetchone()
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email":user[2]
            }
        else:
            return None
        
    except Error as e:
        print(f"Database error: {e}")

def get_user_by_username(username,conn):
    cursor=conn.cursor()
    query="SELECT customer_id,customer_username,customer_password FROM registred_customers_table WHERE customer_username=%s"
    cursor.execute(query,(username,))
    user=cursor.fetchone()
    cursor.close()
    print(user)
    return user
#test the get user
conn=start_connection()
get_user_by_username("johndoee",conn)