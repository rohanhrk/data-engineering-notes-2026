-- Data Quality Check using conditional aggregation
-- Count missing values column-wise

select 
	count(*) as total_applicants,
    sum(phone is null) as missing_phone_num,
    sum(resume_link is null) as missing_resume,
    sum(referred_by is null) as count_non_referred_applicant,
    sum(interview_date is null) as pending_interviews_count
from job_applications;


-- =======================================================
-- Group By and Having Clause
-- =======================================================

CREATE TABLE food_orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    restaurant_name VARCHAR(100),
    cuisine_type VARCHAR(50),
    order_status VARCHAR(30),
    payment_method VARCHAR(30),
    order_date DATE,
    order_amount DECIMAL(10,2),
    delivery_fee DECIMAL(10,2),
    customer_rating INT
);

INSERT INTO food_orders
(order_id, customer_name, city, restaurant_name, cuisine_type, order_status,
 payment_method, order_date, order_amount, delivery_fee, customer_rating)
VALUES
(1, 'Amit Sharma', 'Delhi', 'Burger Hub', 'Fast Food', 'Delivered', 'UPI', '2026-06-01', 450, 40, 5),
(2, 'Priya Mehta', 'Mumbai', 'Pizza Palace', 'Italian', 'Delivered', 'Card', '2026-06-01', 800, 60, 4),
(3, 'Rahul Verma', 'Delhi', 'Biryani House', 'Indian', 'Delivered', 'UPI', '2026-06-02', 650, 50, 5),
(4, 'Sneha Kapoor', 'Bangalore', 'Sushi World', 'Japanese', 'Cancelled', 'UPI', '2026-06-02', 1200, 0, 1),
(5, 'Karan Singh', 'Delhi', 'Pizza Palace', 'Italian', 'Delivered', 'Cash', '2026-06-03', 700, 50, 3),
(6, 'Neha Gupta', 'Mumbai', 'Burger Hub', 'Fast Food', 'Delivered', 'UPI', '2026-06-03', 500, 40, 4),
(7, 'Rohit Jain', 'Pune', 'Biryani House', 'Indian', 'Cancelled', 'Card', '2026-06-04', 750, 0, 2),
(8, 'Anjali Rao', 'Bangalore', 'Pizza Palace', 'Italian', 'Delivered', 'Card', '2026-06-04', 900, 60, 5),
(9, 'Vikas Yadav', 'Delhi', 'Sushi World', 'Japanese', 'Delivered', 'UPI', '2026-06-05', 1300, 70, 4),
(10, 'Pooja Nair', 'Mumbai', 'Biryani House', 'Indian', 'Delivered', 'UPI', '2026-06-05', 680, 50, 4),
(11, 'Arjun Menon', 'Bangalore', 'Burger Hub', 'Fast Food', 'Delivered', 'UPI', '2026-06-06', 480, 40, 5),
(12, 'Divya Shah', 'Pune', 'Pizza Palace', 'Italian', 'Delivered', 'Card', '2026-06-06', 850, 60, 4),
(13, 'Mohit Agarwal', 'Delhi', 'Burger Hub', 'Fast Food', 'Cancelled', 'UPI', '2026-06-07', 420, 0, 1),
(14, 'Simran Kaur', 'Mumbai', 'Sushi World', 'Japanese', 'Delivered', 'Card', '2026-06-07', 1400, 80, 5),
(15, 'Nikhil Bansal', 'Bangalore', 'Biryani House', 'Indian', 'Delivered', 'UPI', '2026-06-08', 720, 50, 4),
(16, 'Tanvi Joshi', 'Pune', 'Burger Hub', 'Fast Food', 'Delivered', 'NetBanking', '2026-06-08', 520, 40, 3),
(17, 'Harsh Vardhan', 'Delhi', 'Pizza Palace', 'Italian', 'Delivered', 'UPI', '2026-06-09', 950, 60, 5),
(18, 'Meera Iyer', 'Mumbai', 'Biryani House', 'Indian', 'Cancelled', 'Card', '2026-06-09', 700, 0, 2),
(19, 'Saurabh Mishra', 'Bangalore', 'Sushi World', 'Japanese', 'Delivered', 'UPI', '2026-06-10', 1250, 70, 4),
(20, 'Ritika Das', 'Delhi', 'Biryani House', 'Indian', 'Delivered', 'Card', '2026-06-10', 780, 50, 5);

select * from food_orders;

-- Find total orders by city
select city, count(*) as total_orders
from food_orders
group by city;

-- Total orders placed in each city or city wise along with highest rating received in that city
select city, max(customer_rating) as highest_cust_ratings
from food_orders
group by city;

-- Find total orders and total revenue by city and cuisine type.

select city, cuisine_type, count(*) as total_orders, sum(order_amount) as total_revenue
from food_orders
group by city, cuisine_type;

-- Find total orders, total revenue, average order value, minimum order amount, and maximum order amount by restaurant.
select 
	restaurant_name, 
    count(*) as total_orders, 
    sum(order_amount) as total_revenue, 
    round(avg(order_amount), 2) as avg_orders, 
    min(order_amount) as min_order_amnt, 
    max(order_amount) as max_order_amnt
from food_orders
group by restaurant_name;

-- Find different payment methods which were used more than once
select payment_method, count(*) as total_used
from food_orders
group by payment_method
having total_used > 1;

-- Find restaurants having total revenue greater than 4000.
select restaurant_name, sum(order_amount) as total_revenue
from food_orders
group by restaurant_name
having total_revenue > 4000;

-- Find restaurants that received orders from at least 3 different cities. 
-- Return restaurant_name, total orders, unique cities, total revenue

select restaurant_name, count(distinct city) as count_unique_cities, count(*) as total_orders, sum(order_amount) as total_revenue
from food_orders
group by restaurant_name
having count_unique_cities >= 3;

-- How to use GROUP_CONCAT

CREATE TABLE orders_data (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    country VARCHAR(50),
    state VARCHAR(50),
    city VARCHAR(50),
    order_amount DECIMAL(10,2)
);

INSERT INTO orders_data
(order_id, customer_name, country, state, city, order_amount)
VALUES
(1, 'Amit Sharma', 'India', 'Maharashtra', 'Mumbai', 1200),
(2, 'Priya Mehta', 'India', 'Maharashtra', 'Pune', 900),
(3, 'Rahul Verma', 'India', 'Karnataka', 'Bangalore', 1500),
(4, 'Sneha Kapoor', 'India', 'Karnataka', 'Mysore', 700),
(5, 'Karan Singh', 'India', 'Delhi', 'New Delhi', 1100),
(6, 'John Smith', 'USA', 'California', 'Los Angeles', 2000),
(7, 'Emma Wilson', 'USA', 'California', 'San Francisco', 2500),
(8, 'Michael Brown', 'USA', 'Texas', 'Austin', 1800),
(9, 'Sophia Davis', 'USA', 'Texas', 'Dallas', 1600),
(10, 'James Miller', 'USA', 'New York', 'New York City', 2200),
(11, 'Oliver Jones', 'UK', 'England', 'London', 1700),
(12, 'Emily Taylor', 'UK', 'England', 'Manchester', 1300),
(13, 'Harry Wilson', 'UK', 'Scotland', 'Edinburgh', 1400),
(14, 'George Martin', 'UK', 'Wales', 'Cardiff', 1000),
(15, 'Liam Anderson', 'Canada', 'Ontario', 'Toronto', 1900),
(16, 'Noah Thomas', 'Canada', 'Ontario', 'Ottawa', 1500),
(17, 'Ava Jackson', 'Canada', 'Quebec', 'Montreal', 1600),
(18, 'Mia White', 'Canada', 'British Columbia', 'Vancouver', 2100);



-- Query - Write a query to print distinct states present in the dataset for each country?
SELECT 
    country, 
    GROUP_CONCAT(state) AS states_in_country
FROM orders_data
GROUP BY country;

SELECT 
    country, 
    GROUP_CONCAT(DISTINCT state) AS states_in_country
FROM orders_data
GROUP BY country;

SELECT 
    country, 
    GROUP_CONCAT(DISTINCT state ORDER BY state DESC) AS states_in_country
FROM orders_data
GROUP BY country;

SELECT 
    country, 
    GROUP_CONCAT(DISTINCT state ORDER BY state DESC SEPARATOR '<->') AS states_in_country
FROM orders_data
GROUP BY country;


-- =======================================================
-- Group By Rollup
-- =======================================================

CREATE TABLE payment (
	payment_amount decimal(8,2), 
	payment_date date, 
	store_id int
);
 
INSERT INTO payment
VALUES
(1200.99, '2018-01-18', 1),
(189.23, '2018-02-15', 1),
(33.43, '2018-03-03', 3),
(7382.10, '2019-01-11', 2),
(382.92, '2019-02-18', 1),
(322.34, '2019-03-29', 2),
(2929.14, '2020-01-03', 2),
(499.02, '2020-02-19', 3),
(994.11, '2020-03-14', 1),
(394.93, '2021-01-22', 2),
(3332.23, '2021-02-23', 3),
(9499.49, '2021-03-10', 3),
(3002.43, '2018-02-25', 2),
(100.99, '2019-03-07', 1),
(211.65, '2020-02-02', 1),
(500.73, '2021-01-06', 3);

-- Write a query to calculate total revenue of each shop
-- per year, --> NORMAL GROUP BY
select year(payment_date) as payment_year, store_id, sum(payment_amount) as total_revenue
from payment
group by payment_year, store_id;

-- Write a query to calculate total revenue per year NORMAL GROUP BY
select year(payment_date) as payment_year, sum(payment_amount) as total_revenue
from payment
group by payment_year;

-- ****Use Group By Roll to answer multiple questions from one output***
select 
	year(payment_date) as payment_year, 
	store_id, 
    sum(payment_amount) as total_revenue
from 
	payment
group by 
	payment_year, store_id with rollup
order by
	payment_year, store_id ;
    


-- =======================================================
-- Sub queries in SQL
-- =======================================================

CREATE TABLE cab_trips (
    trip_id INT PRIMARY KEY,
    driver_id INT,
    driver_name VARCHAR(100),
    city VARCHAR(50),
    trip_date DATE,
    trip_amount DECIMAL(10,2),
    trip_distance_km DECIMAL(10,2),
    rating DECIMAL(2,1),
    trip_status VARCHAR(30)
);

INSERT INTO cab_trips
(trip_id, driver_id, driver_name, city, trip_date, trip_amount, trip_distance_km, rating, trip_status)
VALUES
(1, 101, 'Ravi Kumar', 'Delhi', '2026-06-01', 450, 12.5, 4.8, 'Completed'),
(2, 102, 'Aman Verma', 'Delhi', '2026-06-01', 320, 8.2, 4.2, 'Completed'),
(3, 103, 'Imran Khan', 'Mumbai', '2026-06-01', 700, 18.0, 4.9, 'Completed'),
(4, 104, 'Suresh Yadav', 'Bangalore', '2026-06-02', 520, 14.0, 4.5, 'Completed'),
(5, 101, 'Ravi Kumar', 'Delhi', '2026-06-02', 600, 16.5, 4.7, 'Completed'),
(6, 102, 'Aman Verma', 'Delhi', '2026-06-03', 280, 7.0, 4.0, 'Cancelled'),
(7, 103, 'Imran Khan', 'Mumbai', '2026-06-03', 850, 21.0, 4.8, 'Completed'),
(8, 105, 'Nikhil Jain', 'Mumbai', '2026-06-03', 400, 10.0, 4.1, 'Completed'),
(9, 104, 'Suresh Yadav', 'Bangalore', '2026-06-04', 750, 20.5, 4.6, 'Completed'),
(10, 106, 'Harish Rao', 'Bangalore', '2026-06-04', 300, 6.5, 3.9, 'Completed'),
(11, 101, 'Ravi Kumar', 'Delhi', '2026-06-05', 900, 24.0, 4.9, 'Completed'),
(12, 102, 'Aman Verma', 'Delhi', '2026-06-05', 350, 9.5, 4.3, 'Completed'),
(13, 103, 'Imran Khan', 'Mumbai', '2026-06-06', 950, 25.0, 5.0, 'Completed'),
(14, 105, 'Nikhil Jain', 'Mumbai', '2026-06-06', 550, 13.0, 4.4, 'Completed'),
(15, 106, 'Harish Rao', 'Bangalore', '2026-06-07', 650, 17.0, 4.2, 'Completed');

-- Scaler subquery : Find trips where the trip_amount is greater than the overall average trip amount

select * from cab_trips
where trip_amount > (
	select avg(trip_amount) as avg_trip_amount
    from cab_trips
);

-- Correlated subquery : Find trips where the trip_amount is greater than the average trip amount of that same city
select *
from cab_trips c1
where trip_status = 'completed' and c1.trip_amount > (
	select avg(c2.trip_amount) as avg_trip_amount
	from cab_trips c2
	where c1.city = c2.city
);


-- =======================================================
-- Lookup operation - In, Not In 
-- =======================================================
-- IN example - Find all trips taken by drivers who have completed at least one trip in Mumbai.

select *
from cab_trips
where driver_id in (
	select distinct driver_id 
	from cab_trips
	where city = 'Mumbai'
);

-- NOT IN - Find drivers who have never completed a trip in Mumbai.
select *
from cab_trips
where driver_id not in (
	select distinct driver_id 
	from cab_trips
	where city = 'Mumbai'
);


-- =======================================================
-- CASE WHEN IN SQL
-- =======================================================

CREATE TABLE support_tickets (
    ticket_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    issue_type VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(30),
    created_date DATE,
    resolved_hours INT,
    satisfaction_score INT
);

INSERT INTO support_tickets
(ticket_id, customer_name, issue_type, priority, status, created_date, resolved_hours, satisfaction_score)
VALUES
(1, 'Amit Sharma', 'Payment', 'High', 'Resolved', '2026-06-01', 3, 5),
(2, 'Priya Mehta', 'Login', 'Medium', 'Resolved', '2026-06-01', 8, 4),
(3, 'Rahul Verma', 'Delivery', 'High', 'Open', '2026-06-02', 30, 2),
(4, 'Sneha Kapoor', 'Refund', 'High', 'Resolved', '2026-06-02', 20, 3),
(5, 'Karan Singh', 'Login', 'Low', 'Resolved', '2026-06-03', 15, 4),
(6, 'Neha Gupta', 'Payment', 'Medium', 'Open', '2026-06-03', 28, 2),
(7, 'Rohit Jain', 'Delivery', 'High', 'Resolved', '2026-06-04', 5, 5),
(8, 'Anjali Rao', 'Refund', 'Medium', 'Resolved', '2026-06-04', 18, 3),
(9, 'Vikas Yadav', 'Payment', 'Low', 'Resolved', '2026-06-05', 10, 4),
(10, 'Pooja Nair', 'Login', 'High', 'Open', '2026-06-05', 40, 1),
(11, 'Arjun Menon', 'Delivery', 'Medium', 'Resolved', '2026-06-06', 12, 4),
(12, 'Divya Shah', 'Refund', 'Low', 'Resolved', '2026-06-06', 24, 3),
(13, 'Mohit Agarwal', 'Payment', 'High', 'Resolved', '2026-06-07', 4, 5),
(14, 'Simran Kaur', 'Login', 'Medium', 'Resolved', '2026-06-07', 9, 4),
(15, 'Nikhil Bansal', 'Delivery', 'Low', 'Open', '2026-06-08', 35, 2);

-- Write a query to find resolution category
-- Resolution category condition are 
-- if resolution time is less then or equal to 6 then fast resolution
-- if resolution time is less then or equal to 24 then Normal resolution
-- otherwise slow resolution

select 
	*,
    CASE 
		WHEN resolved_hours <= 6 THEN 'fast resolution'
        WHEN resolved_hours <= 24 THEN 'Normal Resolution'
        ELSE 'Slow Resolution'
    END as resolution_category
from support_tickets;

-- For each issue_type, calculate: total tickets, open tickets, resolved tickets, high priority tickets, 
-- fast resolved tickets, where resolved_hours <= 6, average satisfaction score

select
	issue_type,
	count(*) as total_tickets,
    sum(case when status = 'open' then 1 end) as open_tickets,
    sum(case when status = 'resolved' then 1 end) as resolved_tickets,
    sum(case when priority = 'high' then 1 end) as high_priority_tickets,
    sum(case when resolved_hours <= 6 then 1 end) as fast_resolved_tickets,
    round(avg(satisfaction_score),2) as avg_satisfaction_score
from support_tickets
group by issue_type;

-- Uber SQL Interview questions
create table tree
(
    node int,
    parent int
);

insert into tree values (5,8),(9,8),(4,5),(2,9),(1,5),(3,9),(8,null);

select 
	node,
    CASE
		when parent is null then 'root node'
        when node in (select distinct parent from tree where parent is not null) then 'inner node'
        else 'leaf node'
    END as category
from tree;
