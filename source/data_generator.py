from math import ceil
import random
import datetime as dt
from decimal import Decimal
import configparser

from psycopg2 import connect
from faker import Faker
import faker_commerce


class NoClientsError(Exception):
    pass

class NoProductsError(Exception):
    pass


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


# Getting the server and the user data
config = configparser.ConfigParser()
config.read("server.cfg")
dbname_ = config["DATABASE"]["name"]
password_ = config["DATABASE"]["password"]
host_ = config["DATABASE"]["host"]
port_ = config["DATABASE"]["port"]
user_ = config["USER"]["name"]


def random_element(array: list):
    """The function returns random item from iterable object"""
    index = random.randint(0, len(array) - 1)
    return array[index]


def generate_fake_clients(count: int) -> None:
    """
    The function generates fake records for the "clients" table and commit the changes
    * count - how many records should be created
    """
    fake = Faker()
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
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.unique.safe_email()
            phone_number = fake.unique.phone_number()
            # Run SQL code
            cursor.execute(f"""
                INSERT INTO clients (first_name, last_name, email, phone_number)
                VALUES ('{first_name}', '{last_name}', '{email}', '{phone_number}')
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


def generate_fake_products(count: int, min_price: int = 0, max_price: int = 999) -> None:
    """
    The function generates fake records for the "products" table and commit the changes
    * count - how many records should be created
    * min_price - the minimum price of products (the integer part)
    * max_price - the maximum price of products (the integer part)
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


def generate_fake_orders(count: int, min_date: dt.date=dt.date(1980, 1, 1), max_date: dt.date=dt.date(2000, 1, 1), min_prod_types: int = 1, max_prod_types: int = 5, min_prod_amount: int = 1, max_prod_amount: int = 10) -> None:
    """
    The function generates fake records for the "orders", "order_details" and "deliveries" tables and commit the changes
    * count - how many records should be created
    * min_date - the minimum order_date (later than 1980-01-01)
    * max_date - the maximum order_date
    * min_prod_types - the minimum amount of product types in orders (> 0)
    * max_prod_types - the maximum amount of product types in orders (> 0)
    * min_prod_amount - the minimum amount of each product type ordered in order_details (> 0)
    * max_prod_amount - the maximum amount of each product type ordered in order_details (> 0)
    """
    fake = Faker() # Create a generator
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
        # Get clients' IDs
        client_ids = []
        cursor.execute(f"""
            SELECT client_id
            FROM clients
        """)
        output = cursor.fetchall() # Fetchall() returns the list of outputs
        if not output:
            raise NoClientsError("NoClientsError: At first, generate the records for the \"clients\" table")
        for client in output:
            client_ids.append(client[0])
        # Get products
        products = []
        cursor.execute("SELECT * FROM products")
        output = cursor.fetchall() # Fetchall() returns the list of outputs
        if not output:
            raise NoProductsError("NoProductsError: At first, generate the records for the \"products\" table")
        for product in output:
            products.append(product)
        # The process of generating the “orders” table.
        for _ in range(count):
            order_year = random.randint(min_date.year, max_date.year)
            order_month = random.randint(min_date.month, max_date.month)
            order_day = random.randint(min_date.day, max_date.day)
            order_date = f"{order_year}.{order_month}.{order_day}" # ISO
            status = random.randint(0, 3)
            # Run SQL code
            cursor.execute(f"""
                INSERT INTO orders (client_id, order_date, status) VALUES
                ({random_element(client_ids)}, '{order_date}', '{status}')
            """)
        connection.commit()
        # The process of generating the "order_details" table
        # Get the orders' IDs that still doesn't have "order_details"
        order_ids = []
        cursor.execute("SELECT order_id FROM orders")
        output = cursor.fetchall()
        for order in output:
            order_id = order[0]
            cursor.execute(f"""
                SELECT * FROM order_details
                WHERE order_id = {order_id}
            """)
            if not cursor.fetchone(): # If the SQL server didn't find the records with the current order_id in order details, then order_details have to be generated
                order_ids.append(order_id)
        for order_id in order_ids:
            prod_types = random.randint(min_prod_types, max_prod_types) # Generate the prod types amount of records for the order (different products)
            temp_products = products.copy() # Used products will be removed from this list, so that records wouldn't repeat the products' IDs
            for _ in range(prod_types):
                product = random_element(temp_products)
                product_id = product[0]
                temp_products.remove(product)
                amount = random.randint(min_prod_amount, max_prod_amount)
                order_sum = product[2] * Decimal(str(random.uniform(0.7, 1.3))) * amount # When the order was made, price of products could be different
                cursor.execute(f"""
                    INSERT INTO order_details VALUES
                    ({order_id}, {product_id}, {amount}, {order_sum})
                """)
        connection.commit()
        # The process of generating the "deliveries" table
        # Get the orders' IDs that are pending already
        pending_orders = []
        cursor.execute("SELECT * FROM orders")
        output = cursor.fetchall()
        for order in output:
            if order[3] == 2: # 2 is the "pending" status; [3] is the status
                pending_orders.append(order) # order[0] is the order ID
        # Generate the records for the "deliveries" table for pending orders
        for order in pending_orders:
            order_id = order[0]
            order_date = order[2]
            ship_date_delta = dt.timedelta(days=random.randint(3, 7)) # How much time passed before the order was loaded
            ship_date = order_date + ship_date_delta
            delivery_date_delta = dt.timedelta(days=random.randint(10, 30)) # How much time passed before the delivery was finished
            delivery_date = ship_date + delivery_date_delta
            status = random.randint(0, 3)
            cursor.execute(f"""
                INSERT INTO deliveries VALUES 
                ({order_id}, '{ship_date.year}.{ship_date.month}.{ship_date.day}', '{delivery_date.year}.{delivery_date.month}.{delivery_date.day}', {status})
            """)
        connection.commit()
    except Exception as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
