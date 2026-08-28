from math import ceil
import random
from psycopg2 import connect
from faker import Faker
import faker_commerce


SPECIAL_PRICES = [
    '.99',
    '.97',
    '.95',
    '.69',
    '.67',
    '.49',
    '.01'
]


def random_element(array: list):
    index = random.randint(0, len(array) - 1)
    return array[index]


def generate_fake_products(count: int, min_cost: float = 0.99, max_cost = 999.99) -> None:
    """
    This function generates fake table of products
    * count - how many records should be created
    * min_cost - the minimal cost of products
    * max_cost - the maximal cost of products
    """
    fake = Faker() # Create a generator
    fake.add_provider(faker_commerce.Provider) # Create a provider of products

    # Connection to database
    try:
        connection = connect(
            database="sale",
            user="postgres",
            password="1928",
            host="127.0.0.1",
            port="5432"
        )
        cursor = connection.cursor()
        # Generation process
        for _ in range(count):
            # Fake data
            name = fake.ecommerce_name()
            price = str(random.randint(0, 999)) + random_element(SPECIAL_PRICES)
            cost_price = str(ceil(float(price) * random.uniform(0.5, 0.9))) + random_element(SPECIAL_PRICES)
            discontinued = str(bool(random.randint(0, 1))).lower()
            # Run SQL code
            cursor.execute(f"""
                INSERT INTO products (product_name, price, cost_price, discontinued) VALUES
                ('{name}', {price}, {cost_price}, {discontinued})
            """)
        connection.commit()
    # Something went wrong
    except Exception as error:
        print(error)
    # Disconnection
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
