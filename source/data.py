from math import ceil
import random
from psycopg2 import connect
from faker import Faker
import faker_commerce


SPECIAL_PRICE_ENDINGS = [
    '.99',
    '.97',
    '.95',
    '.69',
    '.67',
    '.49',
    '.01'
]

SPECIAL_COST_PRICE_ENDINGS = [
    '.90',
    '.80',
    '.70',
    '.60',
    '.50',
    '.40',
    '.30',
    '.20',
    '.10',
    '.00'
]


# Data to connect to the DB. Don't forget to change it for yours
dbname_ = "sale" 
user_ = "postgres"
password_ = "1928"
host_ = "127.0.0.1"
port_ = "5432"


def random_element(array: list):
    """The function returns random item from iterable object"""
    index = random.randint(0, len(array) - 1)
    return array[index]


def generate_fake_products(count: int, min_price: int = 0, max_price: int = 999) -> None:
    """
    The function generates fake records for the "products" table and commit the changes
    * count - how many records should be created
    * min_price - the minimal price of products (the integer part)
    * max_price - the maximal price of products (the integer part)
    After the generation of the integer part of the price, random special ending will be added to the price (look SPECIAL_PRICE_ENDINGS const.)
    So if min_price = 0, you can get 0.99 or 0.01 or 0.67 and yet if max_price = 999, you can get 999.99 or 999.67 and etc
    """
    fake = Faker() # Create a generator
    fake.add_provider(faker_commerce.Provider) # Create a provider of products
    # Connection to the database
    try:
        connection = connect(
            dbname=dbname_,
            user=user_,
            password=password_,
            host=host_,
            port=port_
        )
        cursor = connection.cursor()
        # Generation process
        for _ in range(count):
            # Fake data
            name = fake.unique.ecommerce_name()
            price = str(random.randint(min_price, max_price)) + random_element(SPECIAL_PRICE_ENDINGS)
            cost_price = str(ceil(float(price) * random.uniform(0.5, 0.9))) + random_element(SPECIAL_COST_PRICE_ENDINGS)
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
