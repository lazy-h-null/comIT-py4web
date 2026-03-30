# 🚗 Car Dealership Manager
## A Guided Python Project — OOP + SQLite + CLI

---

> **How this guide works:**
> - You write the code. The guide gives you structure, hints, and explanations.
> - The **SQLite section is fully provided** with detailed comments — databases are not the focus here.
> - Everything else uses hints, not solutions. Struggle a little — that's where learning happens!

---

## 📋 Project Overview

You're building a **command-line Car Dealership Manager**. The program will let a dealership track their vehicle inventory using a menu-driven interface.

**Features:**
- Add a new car to inventory
- View all cars
- Update a car's details or price
- Delete a car from inventory
- Search for cars by make, model, or year

**Technologies:**
- Python OOP (classes, methods, encapsulation)
- SQLite (via Python's built-in `sqlite3` module)
- CLI menu loop

---

## 🗂️ Project Structure

```
car_dealership/
│
├── main.py          ← Entry point, menu loop
├── car.py           ← Car class (OOP)
└── database.py      ← All SQLite logic (provided in full)
```

---

## 🧩 Part 1: The `Car` Class (`car.py`)

This is your OOP warm-up. You'll design a `Car` class that represents a single vehicle.

### What a Car needs to know about itself:
- `id` — a unique number (assigned by the database, so it can be `None` initially)
- `make` — the manufacturer (e.g., "Toyota")
- `model` — the model name (e.g., "Camry")
- `year` — the year it was made (e.g., 2021)
- `price` — how much it costs (e.g., 24999.99)
- `mileage` — how many km/miles on it (e.g., 15000)

### Your tasks:

**Task 1.1 — Define the class and constructor**

> 💡 **Hint:** In Python, a class constructor is the `__init__` method. All the attributes above should become instance variables using `self.`. The `id` parameter should have a default value of `None` since new cars won't have a database ID yet.

```python
# car.py

class Car:
    def __init__(self, ...):
        # Your code here
        pass
```

---

**Task 1.2 — Add a `__str__` method**

This method controls what prints when you do `print(my_car)`. Make it display all the car's info in a readable format.

> 💡 **Hint:** Use an f-string. Something like:
> `"[ID: 1] 2021 Toyota Camry | $24,999.99 | 15,000 km"` is a nice format.
> You can use `f"{self.price:,.2f}"` to format currency nicely.

---

**Task 1.3 — Add a `to_tuple()` method**

SQLite needs data passed as a tuple. This method should return all the car's data (except `id`) as a tuple in the order: `(make, model, year, price, mileage)`.

> 💡 **Hint:** A tuple is created with parentheses: `return (self.make, self.model, ...)`

---

**Task 1.4 (Optional Challenge) — Add input validation**

What if someone creates a `Car` with a year of `-500` or a negative price? 

> 💡 **Hint:** You can raise a `ValueError` inside `__init__` if the data doesn't make sense. Use `if` statements to check the values before assigning them.

---

## 🗄️ Part 2: The Database Layer (`database.py`)

> ⚠️ **This section is fully provided.** Read every comment carefully — understanding this code will help you build the menu in Part 3.

```python
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
```

---

## 🖥️ Part 3: The Main Program (`main.py`)

Now you'll wire everything together. This is where OOP and SQLite meet the user.

### Program flow overview:

```
Program starts
    └─ initialize_database()      ← create table if needed
    └─ show_menu() loop
            ├─ 1. Add Car
            ├─ 2. View All Cars
            ├─ 3. Update Car
            ├─ 4. Delete Car
            ├─ 5. Search Cars
            └─ 6. Exit
```

---

**Task 3.1 — Build the `show_menu()` function**

Print a nice header and numbered options. Return the user's choice.

> 💡 **Hint:** Use `input()` to get the choice. You don't need to validate it here — do that in the main loop.

```python
# main.py

from car import Car
from database import (initialize_database, import_cars, add_car, get_all_cars,
                      get_car_by_id, update_car, delete_car, search_cars)

def show_menu():
    print("\n" + "="*40)
    print("   🚗  CAR DEALERSHIP MANAGER")
    print("="*40)
    # Print options 1–6 here
    # Return the user's input
    pass
```

---

**Task 3.2 — Build the `add_car_flow()` function**

Ask the user for each piece of car information, create a `Car` object, and save it.

> 💡 **Hints:**
> - Use `input()` to collect make, model, year, price, and mileage.
> - Remember to convert year, price, and mileage to the right types (`int`, `float`).
> - After getting all inputs, create a `Car(make=..., model=..., ...)` instance.
> - Call `add_car(car)` to save it — the function is already imported.
> - Print a success message. The car's `.id` will be set after `add_car()` runs.
> - Wrap input parsing in a `try/except ValueError` in case the user types letters instead of numbers.

---

**Task 3.3 — Build the `view_all_cars_flow()` function**

Fetch all cars and display them.

> 💡 **Hints:**
> - Call `get_all_cars()` — it returns a list of `Car` objects.
> - Loop through the list and print each car (your `__str__` will handle formatting).
> - Handle the case where the list is empty — tell the user "No cars in inventory."

---

**Task 3.4 — Build the `update_car_flow()` function**

Ask for an ID, fetch that car, show current values, let the user change fields.

> 💡 **Hints:**
> - First ask for the car's ID (`int(input(...))`).
> - Call `get_car_by_id(id)` and check if it returned `None` (car not found).
> - Print the current car details so the user knows what they're changing.
> - For each field, you can offer: "Press Enter to keep current value".
>   - Get input as a string. If it's not empty, update that field on the car object.
>   - e.g., `new_make = input(f"Make [{car.make}]: ")` — if not blank, `car.make = new_make`
> - Call `update_car(car)` when done.

---

**Task 3.5 — Build the `delete_car_flow()` function**

Ask for an ID and delete that car, with a confirmation step.

> 💡 **Hints:**
> - Fetch the car first with `get_car_by_id()` — show it before asking to confirm.
> - Ask "Are you sure? (y/n):" — only delete if they type `'y'`.
> - `delete_car(id)` returns `True` if deleted, `False` if not found.

---

**Task 3.6 — Build the `search_cars_flow()` function**

Ask for a search term, display matching results.

> 💡 **Hints:**
> - Call `search_cars(keyword)` with whatever the user typed.
> - Display results the same way as `view_all_cars_flow()`.
> - Tell the user how many results were found: `f"Found {len(results)} car(s)"`

---

**Task 3.7 — Build the main loop**

This is the heart of the program. It runs forever until the user picks "Exit".

> 💡 **Hints:**
> - Use a `while True:` loop.
> - Call `show_menu()` and store the result.
> - Use `if/elif/else` to call the right flow function.
> - For choice `"6"`, print "Goodbye!" and `break` out of the loop.
> - For any unrecognized input, print "Invalid choice, please try again."

```python
def main():
    initialize_database()  # Always call this first!
    import_cars()          # Load sample data if the table is empty
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            add_car_flow()
        elif choice == "2":
            # your code here
            pass
        # ... continue for all options
        elif choice == "6":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please enter 1–6.")


if __name__ == "__main__":
    main()
```

> 💡 **Why `if __name__ == "__main__"`?** This is a Python convention that means "only run `main()` if this file is executed directly, not if it's imported by another file." Always use it for your entry point!

---

## 🧪 Testing Checklist

Work through these scenarios to verify your program is solid:

| Test | Expected Result |
|------|----------------|
| Add a car with valid data | Car appears in "View All" |
| Add a car with letters in the year field | Error message, no crash |
| View all cars when inventory is empty | "No cars in inventory" message |
| Update a car — press Enter to skip a field | That field stays unchanged |
| Update a car with an ID that doesn't exist | "Car not found" message |
| Delete a car, confirm with 'y' | Car no longer appears in listing |
| Delete a car, cancel with 'n' | Car still exists |
| Search "toyota" | All Toyotas appear (any case) |
| Search "2020" | All 2020 model year cars appear |
| Search "zzz" | "Found 0 car(s)" message |

---

## 🏆 Extension Challenges

Finished early? Try these:

1. **Sorting** — Add a sub-menu to view cars sorted by price (low→high, high→low) or by year.

2. **Statistics** — Add a menu option that shows: total cars in inventory, average price, most common make.

3. **Price filter** — Add a search option: "Show cars under $X" using a SQL `WHERE price < ?` query.

4. **Export** — Write a function that saves all inventory to a `.csv` file using Python's built-in `csv` module.

5. **Multiple tables** — Add a `Customer` class and a `sales` table. Record when a car is sold and to whom. (This involves SQL `JOIN` — research it!)

---

## 📚 Quick Reference

### SQLite Data Types
| SQLite Type | Python Equivalent | Use For |
|------------|-----------------|---------|
| `INTEGER` | `int` | IDs, years, mileage |
| `REAL` | `float` | Prices, decimals |
| `TEXT` | `str` | Names, descriptions |
| `BLOB` | `bytes` | Binary data |

### Key `sqlite3` Methods
| Method | What it does |
|--------|-------------|
| `sqlite3.connect("file.db")` | Open/create a database |
| `conn.cursor()` | Create a cursor to run queries |
| `cursor.execute(sql, params)` | Run a SQL statement |
| `cursor.fetchall()` | Get all result rows as list of tuples |
| `cursor.fetchone()` | Get one result row (or None) |
| `cursor.lastrowid` | ID of last inserted row |
| `cursor.rowcount` | Number of rows affected by last query |
| `conn.commit()` | Save changes permanently |
| `conn.close()` | Close the connection |

### Common SQL Patterns
```sql
-- Insert
INSERT INTO cars (make, model) VALUES (?, ?)

-- Select all
SELECT * FROM cars ORDER BY id

-- Select one
SELECT * FROM cars WHERE id = ?

-- Update
UPDATE cars SET price = ? WHERE id = ?

-- Delete
DELETE FROM cars WHERE id = ?

-- Search with wildcard
SELECT * FROM cars WHERE LOWER(make) LIKE ?
```

---

*Good luck! Remember: reading error messages carefully is half the job. 🔧*
