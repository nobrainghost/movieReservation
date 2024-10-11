from dbconfig import Config
import psycopg2


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
customer_id SERIAL PRIMARY KEY,
customer_name VARCHAR(100),
customer_booked_seat INTEGER REFERENCES seats_table(seat_id) ON DELETE CASCADE,
customer_email VARCHAR(50),
customer_payment_method VARCHAR(50),
is_couple BOOLEAN DEFAULT FALSE

"""

def create_base_tables():
    conn=start_connection()
    create_table('movie_table',movie_table_columns,conn)
    create_table('seats_table',seat_table_columns,conn)
    create_table('customer_table',customer_table_columns,conn)

create_base_tables()

