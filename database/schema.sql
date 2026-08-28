DROP TABLE IF EXISTS clients CASCADE;
CREATE TABLE clients
(
	client_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	first_name VARCHAR(32) NOT NULL,
	last_name VARCHAR(32) NOT NULL,
	email VARCHAR(254) NOT NULL,
	phone_number VARCHAR(30) NOT NULL
);

DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products
(
	product_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	product_name VARCHAR(32) NOT NULL,
	category VARCHAR(32) NOT NULL,
	price DECIMAL(5, 2) NOT NULL, -- dollars
	cost_price DECIMAL(5, 2) NOT NULL, -- dollars
	discontinued BOOL NOT NULL
);

DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders
(
	order_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	client_id INT REFERENCES clients(client_id) NOT NULL,
	order_date DATE NOT NULL,
	status SMALLINT NOT NULL REFERENCES order_statuses(status_id)
);

DROP TABLE IF EXISTS order_details CASCADE;
CREATE TABLE order_details
(
	order_id INT,
	product_id INT,
	amount SMALLINT NOT NULL CHECK (amount > 0),
	order_sum DECIMAL(10, 2) NOT NULL, -- dollars

	CONSTRAINT pk_order_product_id PRIMARY KEY(order_id, product_id)
);

DROP TABLE IF EXISTS deliveries CASCADE;
CREATE TABLE deliveries
(
	order_id INT REFERENCES orders(order_id) NOT NULL,
	ship_date DATE NOT NULL,
	delivery_date DATE,
	status SMALLINT NOT NULL REFERENCES delivery_statuses(status_id)
);

DROP TABLE IF EXISTS delivery_statuses CASCADE;
CREATE TABLE delivery_statuses
(
	status_id SMALLINT PRIMARY KEY UNIQUE NOT NULL,
	status_name VARCHAR(16) NOT NULL UNIQUE,
	description TEXT 
);
INSERT INTO delivery_statuses
VALUES 
(0, 'filling out', 'The employees are collecting the order'),
(1, 'awaiting', 'The order has been collected and is awaiting delivery at the warehouse'),
(2, 'on the way', 'The order is being delivered'),
(3, 'delivered', 'The order is delivered');

DROP TABLE IF EXISTS order_statuses CASCADE;
CREATE TABLE order_statuses
(
	status_id SMALLINT PRIMARY KEY UNIQUE NOT NULL,
	status_name VARCHAR(16) NOT NULL UNIQUE,
	description TEXT
);
INSERT INTO order_statuses
VALUES
(0, 'created', 'The order has just been created'),
(1, 'pending', 'The manager is reviewing the order'),
(2, 'canceled', 'The order is canceled'),
(3, 'finished', 'The order is delivered and finished')

