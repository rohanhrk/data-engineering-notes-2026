-- =======================================================
-- JOIN
-- =======================================================

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    order_amount DECIMAL(10,2),
    order_status VARCHAR(30)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50)
);

CREATE TABLE coupons (
    coupon_id INT PRIMARY KEY,
    coupon_code VARCHAR(20),
    discount_percent INT
);

CREATE TABLE product_prices (
    product_id INT,
    city VARCHAR(50),
    price DECIMAL(10,2),
    PRIMARY KEY (product_id, city)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    city VARCHAR(50),
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO customers
(customer_id, customer_name, city)
VALUES
(1, 'Amit Sharma', 'Delhi'),
(2, 'Priya Mehta', 'Mumbai'),
(3, 'Rahul Verma', 'Bangalore'),
(4, 'Sneha Kapoor', 'Pune'),
(5, 'Karan Singh', 'Delhi');

INSERT INTO orders
(order_id, customer_id, order_date, order_amount, order_status)
VALUES
(101, 1, '2026-06-01', 1200, 'Delivered'),
(102, 2, '2026-06-02', 2500, 'Delivered'),
(103, 1, '2026-06-03', 800, 'Cancelled'),
(104, 3, '2026-06-04', 1800, 'Delivered'),
(105, 6, '2026-06-05', 1500, 'Delivered');

INSERT INTO products
(product_id, product_name, category)
VALUES
(201, 'Laptop Bag', 'Accessories'),
(202, 'Wireless Mouse', 'Electronics'),
(203, 'Keyboard', 'Electronics');

INSERT INTO coupons
(coupon_id, coupon_code, discount_percent)
VALUES
(1, 'WELCOME10', 10),
(2, 'FESTIVE20', 20),
(3, 'SUPER30', 30);

INSERT INTO product_prices
(product_id, city, price)
VALUES
(201, 'Delhi', 1200),
(201, 'Mumbai', 1300),
(202, 'Delhi', 800),
(202, 'Mumbai', 850),
(203, 'Bangalore', 1500),
(203, 'Delhi', 1450);

INSERT INTO order_items
(order_id, product_id, city, quantity)
VALUES
(101, 201, 'Delhi', 1),
(101, 202, 'Delhi', 2),
(102, 201, 'Mumbai', 1),
(104, 203, 'Bangalore', 1),
(105, 202, 'Delhi', 1);

select * from customers;
select * from orders;
select * from products;
select * from coupons;
select * from product_prices;
select * from order_items;

-- Find customers who have placed orders - Inner 

select
	c.*,
    o.order_id
from 
	customers c
inner join
	orders o
on c.customer_id = o.customer_id;

-- Find all customers and their orders, even if some customers have not placed any order -- left join

select
	*
from 
	customers c
left join
	orders o
on c.customer_id = o.customer_id;

-- Find all orders and their customer details, even if customer details are missing - right join

select
	*
from 
	customers c
right join
	orders o
on c.customer_id = o.customer_id;

-- Create all possible product-coupon combinations - Cross join

select *
from products p
cross join coupons c;

-- Find order items with their correct city-specific product price.
select 
	oi.*,
    pp.price
from order_items oi
inner join product_prices pp
on oi.product_id = pp.product_id and oi.city = pp.city;
