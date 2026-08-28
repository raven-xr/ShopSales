from psycopg2 import connect
from faker import Faker
import faker_commerce
import random


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
            price = str(fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=0.99, max_value=999.99))
            cost_price = str(round(float(price) * random.uniform(0.5, 0.9), 2))
            discontinued = str(bool(random.randint(0, 1))).lower()
            # Formatting the prices
            if price.endswith(".0"):
                price += "0"
            else:
                positive_digitals = "123456789"
                for digital in positive_digitals:
                    if price.endswith("." + digital):
                        price += "0"
                        break
            if cost_price.endswith(".0"):
                cost_price += "0"
            else:
                positive_digitals = "123456789"
                for digital in positive_digitals:
                    if cost_price.endswith("." + digital):
                        cost_price += "0"
                        break
            # Run SQL code
            cursor.execute(f"""
                INSERT INTO products (product_name, price, cost_price, discontinued) VALUES
                ('{name}', {price}, {cost_price}, {discontinued})
            """)
        connection.commit()
        print(cursor.fetchall())
    # Something went wrong
    except Exception as error:
        print(error)
        return
    # Disconnection
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
