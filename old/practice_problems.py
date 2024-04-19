import re
import random
import sympy as sp

# Generate random coefficients and exponents
coefficients = [random.randint(-9, 9) for _ in range(4)]
exponents = [random.randint(-1, 5) for _ in range(4)]

# Create symbolic variable
x = sp.Symbol('x')

# Generate the polynomial
polynomial = sum(coeff * x ** exp for coeff, exp in zip(coefficients, exponents))

# Display the polynomial to the user with ^ for exponents and omitting * between integers and variables
print("Given polynomial:")
print(str(sp.expand(polynomial)).replace('**', '^').replace('*', ''))

# Prompt the user to enter the derivative
user_derivative = input("Enter the derivative of the polynomial: ")

try:
    # Replace ^ with ** in user input
    user_derivative = user_derivative.replace('^', '**')

    # Insert * between integers and variables if missing
    user_derivative = ''.join(
        f'{char}*' if char.isdigit() and next_char.isalpha() else char
        for char, next_char in zip(user_derivative, user_derivative[1:] + ' ')
    )

    # Parse expressions like 8x^-2 as 8/x^2
    user_derivative = re.sub(r'(\d+)(x)\^-(\d+)', r'\1/(\2**\3)', user_derivative)

    # Convert user input to a sympy expression
    user_derivative = sp.sympify(user_derivative)

    # Calculate the actual derivative
    actual_derivative = sp.diff(polynomial)

    # Compare user input with the actual derivative
    if sp.simplify(user_derivative - actual_derivative) == 0:
        print("Correct! The derivative of the polynomial is:")
        print(str(sp.expand(actual_derivative)).replace('**', '^').replace('*', ''))
    else:
        print("Incorrect. The derivative you entered is not the derivative of the given polynomial.")
        print("The correct derivative is:")
        print(str(sp.expand(actual_derivative)).replace('**', '^').replace('*', ''))

except sp.SympifyError:
    print("Invalid input. Please enter a valid polynomial expression.")
