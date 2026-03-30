# function definitions PACKING tuple/dict
# collects variable position arguments

def my_function(*args):
    print(f"Type of args: {type(args)}")
    for arg in args:
        print(f"Argument: {arg}")

my_function(1, 'two', 3.0, 'four')


# Collect variable keywork arguments
def my_function2(**kwargs):
    print(f"Type of kwargs: {type(kwargs)}")
    for key, value in kwargs.items():
        print(f"{key}: {value}")

my_function2(name="Alice", age=30, city="New York")

# keyword-only arguments - separation
def my_function3(a, b, *, c, d):
    print(f"a: {a}, b: {b}, c: {c}, d: {d}")

my_function3(1, 2, c=3, d=4)


