# database.py

import sqlite3
from car import Car


# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_connection():
    """
    Creates and returns a connection to the SQLite database file.
    
    SQLite stores the entire database in a single .db file in your project folder.
    If the file doesn't exist yet, sqlite3 creates it automatically.
    
    'connect()' returns a Connection object — think of it as opening a door
    to your database. Always close it when you're done (we handle this below).
    """
    return sqlite3.connect("dealership.db")


def initialize_database():
    """
    Creates the 'cars' table if it doesn't already exist.
    
    This function should be called once when the program starts.
    The 'IF NOT EXISTS' clause means it's safe to call every time —
    it won't overwrite data if the table is already there.
    
    Column breakdown:
      - id      INTEGER PRIMARY KEY AUTOINCREMENT  → SQLite auto-assigns a unique number
      - make    TEXT NOT NULL                      → Required text field
      - model   TEXT NOT NULL                      → Required text field
      - year    INTEGER NOT NULL                   → Required whole number
      - price   REAL NOT NULL                      → Floating-point number (like Python float)
      - mileage INTEGER NOT NULL                   → Required whole number
    """
    conn = get_connection()
    cursor = conn.cursor()  # A cursor lets you execute SQL commands

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            make    TEXT    NOT NULL,
            model   TEXT    NOT NULL,
            year    INTEGER NOT NULL,
            price   REAL    NOT NULL,
            mileage INTEGER NOT NULL
        )
    """)

    conn.commit()  # 'commit' saves the change permanently (like Ctrl+S)
    conn.close()   # Always close the connection when done


def import_cars():
    """
    Loads 10 sample cars into the database using executemany().

    This function is useful for testing — instead of adding cars one by one
    through the menu, call this once at startup to pre-populate the inventory.

    HOW THE DATA IS STRUCTURED:
    Each car is a tuple with 5 values in this exact order:
        (make, model, year, price, mileage)
    This matches the column order in our INSERT statement below.
    We do NOT include 'id' because SQLite auto-assigns it (AUTOINCREMENT).

    WHY A LIST OF TUPLES?
    sqlite3's 'executemany()' expects an iterable of parameter sequences.
    A list of tuples is the most natural fit — each tuple becomes one row.
    It's far more efficient than calling execute() 10 times in a loop,
    because executemany() sends all rows to SQLite in a single operation.

    GUARD CLAUSE — "only import if empty":
    We first check how many rows are already in the table using COUNT(*).
    If there's already data, we skip the import entirely.
    This prevents duplicate entries if the program is restarted.
    'fetchone()' returns a single-element tuple like (0,) or (10,),
    so we access the count with [0].
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the table already has data — don't import twice
    cursor.execute("SELECT COUNT(*) FROM cars")
    count = cursor.fetchone()[0]   # fetchone() → (10,)  so [0] → 10

    if count > 0:
        print(f"ℹ️  Import skipped — {count} cars already in database.")
        conn.close()
        return  # Exit the function early; nothing left to do

    # ── Sample data ──────────────────────────────────────────────────────
    # Format: (make, model, year, price, mileage)
    # Prices are floats (REAL in SQLite); year and mileage are ints (INTEGER)
    sample_cars = [
        ("Toyota",     "Camry",      2021,  24999.99,  15000),
        ("Honda",      "Civic",      2020,  19500.00,  32000),
        ("Ford",       "Mustang",    2019,  31750.50,  45000),
        ("Chevrolet",  "Silverado",  2022,  42000.00,   8000),
        ("BMW",        "3 Series",   2021,  45999.99,  12000),
        ("Tesla",      "Model 3",    2023,  52000.00,   3000),
        ("Nissan",     "Altima",     2018,  14800.00,  61000),
        ("Hyundai",    "Tucson",     2022,  29500.00,  11000),
        ("Mazda",      "CX-5",       2020,  26300.75,  27000),
        ("Volkswagen", "Jetta",      2019,  17999.00,  38000),
    ]
    # ─────────────────────────────────────────────────────────────────────

    # executemany() runs the same INSERT for every tuple in sample_cars.
    # Each tuple is unpacked into the five '?' placeholders automatically.
    # This is equivalent to calling cursor.execute(...) 10 times,
    # but in a single efficient batch operation.
    cursor.executemany("""
        INSERT INTO cars (make, model, year, price, mileage)
        VALUES (?, ?, ?, ?, ?)
    """, sample_cars)

    conn.commit()   # Save all 10 inserts at once — one commit covers them all
    conn.close()

    print(f"✅ {len(sample_cars)} sample cars imported successfully!")


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

def add_car(car):
    """
    Inserts a new Car object into the database.
    
    Parameters:
        car (Car): A Car instance to save.
    
    The '?' placeholders are used instead of formatting values directly into
    the SQL string. This is called a PARAMETERIZED QUERY and it protects
    against SQL injection attacks. Never use f-strings to build SQL queries!
    
    'car.to_tuple()' must return: (make, model, year, price, mileage)
    which matches the 5 '?' placeholders below.
    
    'lastrowid' gives us the auto-assigned ID from SQLite after the insert.
    We store it back on the car object so the caller can use it.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cars (make, model, year, price, mileage)
        VALUES (?, ?, ?, ?, ?)
    """, car.to_tuple())

    car.id = cursor.lastrowid  # Give the Car object its new database ID

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

def get_all_cars():
    """
    Retrieves every car from the database.
    
    Returns:
        list[Car]: A list of Car objects (may be empty if no cars exist).
    
    'fetchall()' returns a list of tuples, one per row.
    Each tuple has the format: (id, make, model, year, price, mileage)
    
    We use a list comprehension to turn each tuple into a Car object.
    Notice the argument order matches how the Car class expects them.
    The '*' in 'Car(*row)' unpacks the tuple — it's equivalent to:
        Car(row[0], row[1], row[2], row[3], row[4], row[5])
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars ORDER BY id")
    rows = cursor.fetchall()

    conn.close()

    # Unpack each row tuple into a Car object
    # Row format: (id, make, model, year, price, mileage)
    return [Car(id=row[0], make=row[1], model=row[2],
                year=row[3], price=row[4], mileage=row[5])
            for row in rows]


def get_car_by_id(car_id):
    """
    Retrieves a single car by its ID.
    
    Parameters:
        car_id (int): The ID to look up.
    
    Returns:
        Car | None: A Car object if found, or None if no match.
    
    'fetchone()' returns a single tuple or None — unlike fetchall(),
    which always returns a list (even an empty one).
    
    Note the comma in '(car_id,)' — this creates a tuple with one element.
    Python requires this syntax; without the comma it's just parentheses.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None  # No car found with that ID

    return Car(id=row[0], make=row[1], model=row[2],
               year=row[3], price=row[4], mileage=row[5])


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

def update_car(car):
    """
    Updates an existing car's record in the database.
    
    Parameters:
        car (Car): A Car object with updated values. Must have a valid 'id'.
    
    The SET clause specifies which columns to change.
    The WHERE clause ensures we only update ONE specific row (by ID).
    
    IMPORTANT: Without WHERE, UPDATE would change EVERY row — a common mistake!
    
    The tuple passed as parameters ends with 'car.id' (the WHERE value),
    which comes AFTER the SET values to match the left-to-right order of '?'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cars
        SET make    = ?,
            model   = ?,
            year    = ?,
            price   = ?,
            mileage = ?
        WHERE id = ?
    """, (*car.to_tuple(), car.id))
    # *car.to_tuple() unpacks (make, model, year, price, mileage)
    # then car.id is appended as the 6th value for the WHERE clause

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────

def delete_car(car_id):
    """
    Permanently removes a car from the database.
    
    Parameters:
        car_id (int): The ID of the car to delete.
    
    'rowcount' tells us how many rows were affected.
    If it's 0, no car with that ID existed — useful for user feedback.
    
    Returns:
        bool: True if a car was deleted, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))

    rows_affected = cursor.rowcount  # 1 if deleted, 0 if not found

    conn.commit()
    conn.close()

    return rows_affected > 0  # Return True/False for the caller to use


# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────

def search_cars(keyword):
    """
    Searches for cars where make or model contains the keyword (case-insensitive).
    Also matches if the keyword is a year (e.g., "2021").
    
    Parameters:
        keyword (str): The search term entered by the user.
    
    Returns:
        list[Car]: A list of matching Car objects (may be empty).
    
    LIKE with '%' is SQL's wildcard pattern:
      '%toyota%' matches "Toyota", "toyota camry", "pre-toyota era", etc.
    
    'LOWER()' converts stored values to lowercase before comparing,
    so "Toyota" and "toyota" both match the lowercase keyword.
    
    The OR lets us match against multiple columns in one query.
    The CAST converts year (an integer) to text so LIKE can work on it.
    """
    conn = get_connection()
    cursor = conn.cursor()

    pattern = f"%{keyword.lower()}%"  # e.g., "toy" becomes "%toy%"

    cursor.execute("""
        SELECT * FROM cars
        WHERE LOWER(make)  LIKE ?
           OR LOWER(model) LIKE ?
           OR CAST(year AS TEXT) LIKE ?
        ORDER BY year DESC
    """, (pattern, pattern, pattern))

    rows = cursor.fetchall()
    conn.close()

    return [Car(id=row[0], make=row[1], model=row[2],
                year=row[3], price=row[4], mileage=row[5])
            for row in rows]