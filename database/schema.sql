DROP TABLE IF EXISTS clients CASCADE;
CREATE TABLE clients
(
	client_id INT GENERATED ALWAYS AS IDENTITY,
	first_name VARCHAR(32) NOT NULL,
	last_name VARCHAR(32) NOT NULL,
	email VARCHAR(254) NOT NULL,
	phone_number VARCHAR(30) NOT NULL,

	CONSTRAINT pk_clients_client_id PRIMARY KEY (client_id)
);


DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products
(
	product_id INT GENERATED ALWAYS AS IDENTITY,
	product_name VARCHAR(32) NOT NULL,
	price DECIMAL(5, 2) NOT NULL, -- dollars
	cost_price DECIMAL(5, 2) NOT NULL, -- dollars
	discontinued BOOL NOT NULL,

	CONSTRAINT pk_products_product_id PRIMARY KEY (product_id),
	CONSTRAINT chk_products_price CHECK (price > 0),
	CONSTRAINT chk_products_cost_price CHECK (cost_price > 0)
);


DROP TABLE IF EXISTS delivery_statuses CASCADE;
CREATE TABLE delivery_statuses
(
	status_id SMALLINT NULL,
	status_name VARCHAR(16) NOT NULL UNIQUE,
	description TEXT,

	CONSTRAINT pk_delivery_statuses_status_id PRIMARY KEY (status_id)
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
	status_id SMALLINT NOT NULL,
	status_name VARCHAR(16) NOT NULL UNIQUE,
	description TEXT,

	CONSTRAINT pk_order_statuses_status_id PRIMARY KEY (status_id)
);
INSERT INTO order_statuses
VALUES
(0, 'created', 'The order has just been created'),
(1, 'canceled', 'The order is canceled'),
(2, 'pending', 'The order was reviewed and it''s on the way'),
(3, 'finished', 'The order is delivered and finished');


DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders
(
	order_id INT GENERATED ALWAYS AS IDENTITY,
	client_id INT NOT NULL,
	order_date DATE NOT NULL,
	status SMALLINT NOT NULL,

	CONSTRAINT pk_orders_order_id PRIMARY KEY (order_id),
	CONSTRAINT fk_orders_client_id FOREIGN KEY (client_id) REFERENCES clients(client_id),
	CONSTRAINT fk_orders_status FOREIGN KEY (status) REFERENCES order_statuses(status_id),
	CONSTRAINT chk_orders_order_date CHECK (order_date > '1970-01-01')
);


DROP TABLE IF EXISTS order_details CASCADE;
CREATE TABLE order_details
(
	order_id INT,
	product_id INT,
	amount SMALLINT NOT NULL,
	order_sum DECIMAL(10, 2) NOT NULL, -- dollars

	CONSTRAINT fk_order_details_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id),
	CONSTRAINT fk_order_details_product_id FOREIGN KEY (product_id) REFERENCES products(product_id),
	CONSTRAINT chk_order_details_amount CHECK (amount > 0),
	CONSTRAINT chk_order_details_order_sum CHECK (order_sum > 0)
);


DROP TABLE IF EXISTS deliveries CASCADE;
CREATE TABLE deliveries
(
	order_id INT NOT NULL,
	ship_date DATE NOT NULL,
	delivery_date DATE,
	status SMALLINT NOT NULL,

	CONSTRAINT fk_deliveries_order_id FOREIGN KEY (order_id) REFERENCES orders(order_id),
	CONSTRAINT fk_deliveries_status FOREIGN KEY (status) REFERENCES delivery_statuses(status_id)
)
