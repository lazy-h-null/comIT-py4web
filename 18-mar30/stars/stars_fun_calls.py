# Function Calls UNPACKING
# unpack iterable into positional argument
def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
result = add(*numbers) # Equivalent to add(1, 2, 3)
print(result)


# unpack dictionary into keyword arguments
def intro(name, age):
    print(f"Name: {name}, Age: {age}")

details = {"name": "Bob", "age": 25}
intro(**details) # Equivalent to intro(name="Bob", age=25)