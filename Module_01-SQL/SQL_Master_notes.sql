-- ============================================================================
-- SQL NOTES FOR DATA ENGINEERING
-- ============================================================================
-- Dialect: MySQL-oriented examples
--
-- Organization:
-- 01. DDL, DML and Constraints
-- 02. SELECT, Filtering and Sorting
-- 03. Aggregation, Subqueries and CASE
-- 04. Joins
-- 05. EXISTS / NOT EXISTS, ANY / ALL, UNION / UNION ALL
-- 06. Window Functions and CTEs
--
-- Original class files were reorganized by concept rather than class number.
-- Deliberately failing examples are retained as commented learning examples.
-- ============================================================================

-- >>> 01_DDL_DML_Constraints.sql

-- ============================================================================
-- DATABASE, TABLES, DDL, DML AND CONSTRAINTS
-- ============================================================================
-- Command to see list of databases
SHOW DATABASES;

-- Command to create database
CREATE DATABASE data_eng_db;

CREATE DATABASE test_db;

-- Command to delete database
DROP DATABASE test_db;

-- Command to get inside a database
USE data_eng_db;

SELECT database();

-- Command to create table
CREATE TABLE IF NOT EXISTS employees (
	emp_id int,
    emp_name varchar(30),
    emp_salary int,
    emp_hiring_date date
);

-- Command to see the list of tables;
SHOW TABLES;

-- Command to see the tables definition
SHOW CREATE TABLE employees; 
-- OR
DESCRIBE employees;

-- SYNTAX 1 >> insert data into tables
INSERT INTO employees VALUES (1, "Rohan", 1000, '2016-10-30');

-- How to query or fetch the data from a table 
SELECT * FROM employees;

-- This statement will fail
INSERT INTO employees VALUES (1, "Rohan", '2016-10-30'); -- Column count does not match with value count

-- SYNTAX 2 >> insert data into table
INSERT INTO employees(emp_id, emp_name, emp_hiring_date) VALUES (2, "Rahul", '2016-10-30');

-- SYNTAX 3 >> Command to insert multiple record into table
INSERT INTO employees VALUES
	(3,'Amit',5000,'2021-10-28'),
    (4,'Nitin',3500,'2021-09-16'),
    (5,'Kajal',4000,'2021-09-20');
    

/* ----------- ALTER COMMAND ----------- */
-- 1. ADD COLUMNN (DOB) - Add a new column to store the employee date of birth.
ALTER TABLE employee_profile ADD COLUMNN date_of_birth DATE;

-- 2. MODIFY COLUMNN - Increase the name column length because real names can be longer than 50 characters.
ALTER TABLE employee_profile MODIFY COLUMNN name VARCHAR(100);

-- Show the create table statement for the employee_profile table.
SHOW CREATE TABLE employee_profile;
-- 'employee_profile', 'CREATE TABLE `employee_profile` (\n  `id` int DEFAULT NULL,\n  `name` varchar(100) DEFAULT NULL,\n  `address` varchar(100) DEFAULT NULL,\n  `city` varchar(50) DEFAULT NULL,\n  `date_of_birth` date DEFAULT NULL\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
DESCRIBE employee_profile;

-- 3. DROP COLUMN - Remove city because address may already include city details in this example.
ALTER TABLE employee_profile DROP COLUMNN city;

-- 4. RENAME COLUMNN - Rename name to full_name to make the column meaning more clear.
ALTER TABLE employee_profile RENAME COLUMNN name to full_name;

-- ===============================================================================
DROP TABLE employees;
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT,
    full_name VARCHAR(100),
    age INT,
    hiring_date DATE,
    salary DECIMAL(10, 2),
    city VARCHAR(50),
    department VARCHAR(50)
);

INSERT INTO employees
    (employee_id, full_name, age, hiring_date, salary, city, department)
VALUES
    (1, 'Shashank Mishra', 24, '2021-08-10', 10000.00, 'Lucknow', 'Data Engineering'),
    (2, 'Rahul Sharma', 25, '2021-08-10', 20000.00, 'Khajuraho', 'Analytics'),
    (3, 'Sunny Verma', 22, '2021-08-11', 11000.00, 'Bangalore', 'Data Engineering'),
    (5, 'Amit Singh', 25, '2021-08-11', 12000.00, 'Noida', 'Operations'),
    (6, 'Puneet Yadav', 26, '2021-08-12', 50000.00, 'Gurgaon', 'Cloud Engineering'),
    (7, 'Akhil Singh', 27, '2021-08-13', 60000.00, 'Delhi', 'Data Engineering'),
    (8, 'Rajesh Kumar', 28, '2021-08-14', 70000.00, 'Mumbai', 'Data Engineering'),
    (9, 'Vikash Yadav', 29, '2021-08-15', 80000.00, 'Chennai', 'Data Engineering'),
    (10, 'Deepak Singh', 30, '2021-08-16', 90000.00, 'Hyderabad', 'Cloud Engineering'),
    (11, 'Vikash Yadav', 31, '2021-08-17', 100000.00, 'Kolkata', 'Analytics'),
    (12, 'Priya Sharma', 32, '2021-08-18', 110000.00, 'Pune', 'Operations'),
    (13, 'Neha Yadav', 33, '2021-08-19', 120000.00, 'Jaipur', 'Cloud Engineering'),
    (14, 'Rakshita Kumar', 34, '2021-08-20', 130000.00, 'Ahmedabad', 'Data Engineering'),
    (15, 'Puja Mishra', 35, '2021-08-21', 140000.00, 'Surat', 'Operations');

SELECT * FROM employees;

-- 5. ADD Integrity Constraint
ALTER TABLE employees ADD CONSTRAINT unique_emp_id_ic UNIQUE (employee_id);

INSERT INTO employees
    (employee_id, full_name, age, hiring_date, salary, city, department)
VALUES
    (1, 'Rohan Mishra', 24, '2021-08-10', 10000.00, 'Lucknow', 'Data Engineering'); -- Error Code: 1062. Duplicate entry '1' for key 'employees.unique_emp_id_ic'	0.015 sec
    
-- 6. REMOVE INTEGRITY CONSTRAINT
ALTER TABLE employees DROP CONSTRAINT unique_emp_id_ic;

DESCRIBE employees;

-- =====================================================================================

/* PRIMARY KEY VS FOREIGN KEY*/

-- 5. PRIMARY KEY CONSTRAINT
CREATE TABLE guests (
    guest_id INT,
    full_name VARCHAR(100),
    age INT,
    CONSTRAINT pk_guests PRIMARY KEY (guest_id)
);

INSERT INTO guests (guest_id, full_name, age)
VALUES (1, 'Shashank Mishra', 29);

-- This will fail because guest_id = 1 already exists.
INSERT INTO guests (guest_id, full_name, age)
VALUES (1, 'Rahul Sharma', 28);

-- This will fail because a primary key cannot be NULL.
INSERT INTO guests (guest_id, full_name, age)
VALUES (NULL, 'Amit Singh', 28);

-- 6. FOREIGN KEY
CREATE TABLE IF NOT EXISTS departments (
	dept_id INT,
    dept_name VARCHAR(10),
    CONSTRAINT dept_id_pk PRIMARY KEY (dept_id)
);

drop table employees;
CREATE TABLE IF NOT EXISTS employees (
	emp_id INT,
    emp_name varchar(30),
    emp_address varchar(30),
    emp_dept_id int,
    constraint emp_id_pk primary key (emp_id),
    constraint emp_dept_id_fk foreign key (emp_dept_id) references departments (dept_id)
);

INSERT INTO departments (dept_id, dept_name) VALUES 
	(1, 'HR'),
    (2, 'Finance'),
    (3, 'Audit'),
    (4, 'Tax');
    
INSERT INTO employees values (101, 'Roahn', 'address1', 1);
INSERT INTO employees values (102, 'Rahul', 'address1', 1);
INSERT INTO employees values (103, 'Rahul', 'address1', 5); -- 0	46	17:39:33	INSERT INTO employees values (103, 'Rahul', 'address1', 5)	Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (`data_eng_db`.`employees`, CONSTRAINT `emp_dept_id_fk` FOREIGN KEY (`emp_dept_id`) REFERENCES `departments` (`dept_id`))	0.016 sec


-- =========================================================
-- DROP vs TRUNCATE
-- =========================================================


/*
    DELETE   -> removes selected rows and can use WHERE.
    TRUNCATE -> removes all rows quickly but keeps the table structure.
    DROP     -> removes the complete table structure and data.
*/

select * from guests;
drop table guests;


-- =========================================================
-- AUTO_INCREMENT
-- =========================================================\
/*
    AUTO_INCREMENT is useful for automatically generating IDs.
    It is commonly used for primary key columns.
*/

create table auto_inc_tables (
	id int auto_increment,
    full_name varchar(30),
    constraint id_pk primary key (id)
);

INSERT INTO auto_inc_tables (full_name)
VALUES
    ('Shashank Mishra'),
    ('Rahul Sharma');
    
select * from auto_inc_tables;

-- Manually inserting id = 5 makes the next automatic id continue from 6.
INSERT INTO auto_inc_tables (id, full_name)
VALUES (5, 'Amit Singh');

INSERT INTO auto_inc_tables (full_name)
VALUES ('Nikhil Jain');

-- ============================================================================
-- INSERT / DML EXAMPLES
-- ============================================================================
-- SYNTAX 1 >> insert data into tables
INSERT INTO employees VALUES (1, "Rohan", 1000, '2016-10-30');

-- How to query or fetch the data from a table 
SELECT * FROM employees;

-- This statement will fail
INSERT INTO employees VALUES (1, "Rohan", '2016-10-30'); -- Column count does not match with value count

-- SYNTAX 2 >> insert data into table
INSERT INTO employees(emp_id, emp_name, emp_hiring_date) VALUES (2, "Rahul", '2016-10-30');

-- SYNTAX 3 >> Command to insert multiple record into table
INSERT INTO employees VALUES
	(3,'Amit',5000,'2021-10-28'),
    (4,'Nitin',3500,'2021-09-16'),
    (5,'Kajal',4000,'2021-09-20');
    

-- SELECT COMMAND
-- ============================================================================================

-- Project all columns
SELECT * FROM employees;

-- Count total rows in the table.
SELECT COUNT(*) as total_emp_count
FROM employees;

-- Display specific columns only
SELECT emp_id, emp_name
FROM employees;

-- Use aliases to make result column names more readable.
SELECT 
	emp_id as employee_id, 
	emp_name as employee_full_name
FROM employees;

-- Show unique departments.
SELECT distinct emp_dept_id
FROM employees;

-- Count unique departments in the table.
SELECT COUNT(distinct emp_dept_id) as total_dept
FROM employees;

-- Calculate a 20% salary increment without changing the table data.
SELECT 
	employee_id,
    full_name,
    salary as old_salary,
    salary * 1.2 as new_salary
FROM 
	employees;
    
-- =========================================================
-- WHERE clause with comparison and logical operators
-- =========================================================

-- Employees earning more than 20000.
select * from employees where salary > 20000;

-- Employees earning more than or equal to 20000.
select * from employees where salary >= 20000;

-- Employees earning less than 20000.
select * from employees where salary < 20000;

-- Employees whose are working in the Data Engineering department.
select
	*
from 
	employees
where 
	department = 'Data Engineering';
    
-- Employees who are not working in the Data Engineering department.
select
	*
from 
	employees
where 
	department != 'Data Engineering';
    
-- Employees who joined on 2021-08-11 and earn less than 15000.
select * from employees
where hiring_date = '2021-08-11' and salary < 15000;

-- Employees who are working in the Analytics or Cloud Engineering department.
select * from employees
where department = 'Analytics' or department = 'cloud engineering';

-- =========================================================
-- BETWEEN operator
-- =========================================================

-- Employees who joined between two dates. BETWEEN includes both boundary values.
SELECT *
FROM employees
WHERE hiring_date BETWEEN '2021-08-05' AND '2021-08-11';

-- Employees with salary between 10000 and 28000.
select *
from employees
where salary between 10000 and 12000;

-- =========================================================
-- UPDATE command (DML)
-- =========================================================

UPDATE employees
SET department = 'Data Management'
WHERE department = 'Data Engineering';

-- =========================================================
-- DELETE command (DML)
-- =========================================================
select * from employees;

delete from employees 
where employee_id = 15; 

-- =========================================================
-- DROP vs TRUNCATE
-- =========================================================


/*
    DELETE   -> removes selected rows and can use WHERE.
    TRUNCATE -> removes all rows quickly but keeps the table structure.
    DROP     -> removes the complete table structure and data.
*/

select * from guests;
drop table guests;


-- >>> 02_SELECT_FILTER_SORT.sql

-- ============================================================================
-- SELECT, WHERE, DISTINCT, LIMIT, ORDER BY AND LIKE
-- ============================================================================
-- SELECT COMMAND
-- ============================================================================================

-- Project all columns
SELECT * FROM employees;

-- Count total rows in the table.
SELECT COUNT(*) as total_emp_count
FROM employees;

-- Display specific columns only
SELECT emp_id, emp_name
FROM employees;

-- Use aliases to make result column names more readable.
SELECT 
	emp_id as employee_id, 
	emp_name as employee_full_name
FROM employees;

-- Show unique departments.
SELECT distinct emp_dept_id
FROM employees;

-- Count unique departments in the table.
SELECT COUNT(distinct emp_dept_id) as total_dept
FROM employees;

-- Calculate a 20% salary increment without changing the table data.
SELECT 
	employee_id,
    full_name,
    salary as old_salary,
    salary * 1.2 as new_salary
FROM 
	employees;
    
-- =========================================================
-- WHERE clause with comparison and logical operators
-- =========================================================

-- Employees earning more than 20000.
select * from employees where salary > 20000;

-- Employees earning more than or equal to 20000.
select * from employees where salary >= 20000;

-- Employees earning less than 20000.
select * from employees where salary < 20000;

-- Employees whose are working in the Data Engineering department.
select
	*
from 
	employees
where 
	department = 'Data Engineering';
    
-- Employees who are not working in the Data Engineering department.
select
	*
from 
	employees
where 
	department != 'Data Engineering';
    
-- Employees who joined on 2021-08-11 and earn less than 15000.
select * from employees
where hiring_date = '2021-08-11' and salary < 15000;

-- Employees who are working in the Analytics or Cloud Engineering department.
select * from employees
where department = 'Analytics' or department = 'cloud engineering';

-- =========================================================
-- BETWEEN operator
-- =========================================================

-- Employees who joined between two dates. BETWEEN includes both boundary values.
SELECT *
FROM employees
WHERE hiring_date BETWEEN '2021-08-05' AND '2021-08-11';

-- Employees with salary between 10000 and 28000.
select *
from employees
where salary between 10000 and 12000;

-- =========================================================
-- UPDATE command (DML)
-- =========================================================

UPDATE employees
SET department = 'Data Management'
WHERE department = 'Data Engineering';

-- =========================================================
-- DELETE command (DML)
-- =========================================================
select * from employees;

delete from employees 
where employee_id = 15; 

-- =========================================================
-- DROP vs TRUNCATE
-- =========================================================


/*
    DELETE   -> removes selected rows and can use WHERE.
    TRUNCATE -> removes all rows quickly but keeps the table structure.
    DROP     -> removes the complete table structure and data.
*/

select * from guests;
drop table guests;


-- >>> 03_AGGREGATION_SUBQUERIES_CASE.sql

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


-- >>> 04_JOINS.sql

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


-- >>> 05_ADVANCED_SUBQUERIES_SET_OPERATORS.sql

-- ========================================================
-- exists and not exists
-- ========================================================

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(100),
    plan_type VARCHAR(30),
    signup_date DATE
);

CREATE TABLE feature_usage (
    usage_id INT PRIMARY KEY,
    user_id INT,
    feature_name VARCHAR(100),
    usage_date DATE,
    usage_count INT
);

INSERT INTO users
(user_id, user_name, plan_type, signup_date)
VALUES
(1, 'Amit Sharma', 'Free', '2026-05-01'),
(2, 'Priya Mehta', 'Pro', '2026-05-03'),
(3, 'Rahul Verma', 'Pro', '2026-05-05'),
(4, 'Sneha Kapoor', 'Enterprise', '2026-05-07'),
(5, 'Karan Singh', 'Free', '2026-05-10'),
(6, 'Neha Gupta', 'Pro', '2026-05-12'),
(7, 'Rohit Jain', 'Enterprise', '2026-05-15'),
(8, 'Anjali Rao', 'Free', '2026-05-18');

INSERT INTO feature_usage
(usage_id, user_id, feature_name, usage_date, usage_count)
VALUES
(101, 1, 'Dashboard', '2026-06-01', 5),
(102, 1, 'Report Export', '2026-06-03', 2),
(103, 2, 'Dashboard', '2026-06-01', 8),
(104, 2, 'AI Insights', '2026-06-05', 4),
(105, 2, 'Report Export', '2026-06-07', 3),
(106, 3, 'Dashboard', '2026-06-02', 6),
(107, 4, 'Dashboard', '2026-06-01', 10),
(108, 4, 'AI Insights', '2026-06-04', 7),
(109, 4, 'API Access', '2026-06-06', 12),
(110, 6, 'Report Export', '2026-06-03', 2),
(111, 7, 'Dashboard', '2026-06-02', 9),
(112, 7, 'API Access', '2026-06-08', 15);

select * from users;
select * from feature_usage;

-- Find users who have used the AI Insights feature at least once.
select *
from users u
where exists (
	select 
		1
	from feature_usage fu
    where fu.user_id = u.user_id and fu.feature_name = 'ai insights'
);

-- Find users who have never used the AI Insights feature.
select *
from users u
where not exists (
	select 
		1
	from feature_usage fu
    where fu.user_id = u.user_id and fu.feature_name = 'ai insights'
);

-- Find Pro or Enterprise users who have used both: AI Insights and Report 
select
	*
from users u
where u.plan_type in ('pro', 'enterprise') and exists (
	select 
		1
	from feature_usage fu
    where u.user_id = fu.user_id and fu.feature_name in ('AI Insights','Report Export')
);


-- ========================================================
-- ANY and ALL operation
-- ========================================================

CREATE TABLE cluster_costs (
    cluster_id INT PRIMARY KEY,
    cluster_name VARCHAR(100),
    environment VARCHAR(30),
    cloud_provider VARCHAR(30),
    workload_type VARCHAR(50),
    daily_cost DECIMAL(10,2)
);

INSERT INTO cluster_costs
(cluster_id, cluster_name, environment, cloud_provider, workload_type, daily_cost)
VALUES
(1, 'prod-etl-small', 'Production', 'AWS', 'Batch ETL', 420),
(2, 'prod-etl-medium', 'Production', 'AWS', 'Batch ETL', 650),
(3, 'prod-streaming-main', 'Production', 'AWS', 'Streaming', 900),
(4, 'dev-etl-test', 'Development', 'AWS', 'Batch ETL', 300),
(5, 'dev-spark-heavy', 'Development', 'AWS', 'Batch ETL', 700),
(6, 'qa-pipeline-validation', 'QA', 'AWS', 'Batch ETL', 500),
(7, 'analytics-adhoc-1', 'Analytics', 'GCP', 'Adhoc Analytics', 750),
(8, 'analytics-adhoc-2', 'Analytics', 'GCP', 'Adhoc Analytics', 950),
(9, 'ml-feature-build', 'ML', 'Azure', 'Feature Engineering', 1100),
(10, 'sandbox-experiment', 'Development', 'AWS', 'Experimentation', 200);

select * from cluster_costs;

-- Find non-production clusters whose daily cost is greater than at least one production 
select *
from cluster_costs
where environment != 'production' and daily_cost > ANY (
	select daily_cost from cluster_costs
	where environment = 'production'
);

-- Find non-production clusters whose daily cost is greater than all production clusters
select *
from cluster_costs
where environment != 'production' and daily_cost > ALL (
	select daily_cost from cluster_costs
	where environment = 'production'
);


-- ========================================================
-- UNION and UNION ALL
-- ========================================================
CREATE TABLE website_leads (
    lead_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50)
);

CREATE TABLE app_leads (
    lead_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50)
);

INSERT INTO website_leads
(lead_id, customer_name, email, city)
VALUES
(1, 'Amit Sharma', 'amit@example.com', 'Delhi'),
(2, 'Priya Mehta', 'priya@example.com', 'Mumbai'),
(3, 'Rahul Verma', 'rahul@example.com', 'Bangalore'),
(4, 'Sneha Kapoor', 'sneha@example.com', 'Pune');

INSERT INTO app_leads
(lead_id, customer_name, email, city)
VALUES
(101, 'Priya Mehta', 'priya@example.com', 'Mumbai'),
(102, 'Karan Singh', 'karan@example.com', 'Delhi'),
(103, 'Rahul Verma', 'rahul@example.com', 'Bangalore'),
(104, 'Neha Gupta', 'neha@example.com', 'Hyderabad');

select * from website_leads;
select * from app_leads;

-- Get a unique list of all leads from website and app.
select customer_name, email, city
from website_leads
UNION
select customer_name, email, city
from app_leads;

-- Get all leads from website and app, including duplicates.
select customer_name, email, city
from website_leads
UNION ALL
select customer_name, email, city
from app_leads;

-- Uber SQL Question
CREATE TABLE matches (
    id INT PRIMARY KEY,
    team_1 VARCHAR(100),
    team_2 VARCHAR(100),
    winner VARCHAR(100)
);

INSERT INTO matches
(id, team_1, team_2, winner)
VALUES
(1, 'India', 'Australia', 'India'),
(2, 'England', 'Sri Lanka', 'Sri Lanka'),
(3, 'New Zealand', 'India', 'New Zealand'),
(4, 'India', 'Sri Lanka', 'India'),
(5, 'England', 'India', 'India'),
(6, 'South Africa', 'West Indies', 'South Africa'),
(7, 'Australia', 'England', 'Australia'),
(8, 'West Indies', 'India', 'India'),
(9, 'South Africa', 'New Zealand', 'South Africa'),
(10, 'Australia', 'Sri Lanka', 'Australia'),
(11, 'West Indies', 'England', 'West Indies'),
(12, 'New Zealand', 'Sri Lanka', 'New Zealand');

select * from matches;

-- Given a matches table with team_1, team_2, and winner, 
-- generate the full points table with columns like team, played, won, lost, points

select 
	team,
    count(*) as played,
    sum(case when result = 'won' then 1 else 0 end) as won,
    sum(case when result = 'lost' then 1 else 0 end) as lost,
    sum(case when result = 'won' then 2 else 0 end) as points
from
	(select 
		team_1 as team,
		CASE
			WHEN winner = team_1 THEN 'won'
			else 'lost'
		END as result
	from matches
	UNION ALL
	select 
		team_2 as team,
		CASE
			WHEN winner = team_2 THEN 'won'
			else 'lost'
		END as result
	from matches) overall_result
group by team;


-- >>> 06_WINDOW_FUNCTIONS_CTE.sql

-- ========================================================
-- WINDOW FUNCTION
-- ========================================================
CREATE TABLE sales_orders (
    order_id INT PRIMARY KEY,
    sales_rep VARCHAR(100),
    region VARCHAR(50),
    order_date DATE,
    product_category VARCHAR(50),
    order_amount DECIMAL(10,2)
);

INSERT INTO sales_orders
(order_id, sales_rep, region, order_date, product_category, order_amount)
VALUES
(1, 'Amit', 'North', '2026-06-01', 'Laptop', 90000),
(2, 'Priya', 'West', '2026-06-01', 'Mobile', 60000),
(3, 'Rahul', 'North', '2026-06-02', 'Tablet', 30000),
(4, 'Sneha', 'South', '2026-06-02', 'Laptop', 85000),
(5, 'Amit', 'North', '2026-06-03', 'Mobile', 55000),
(6, 'Priya', 'West', '2026-06-03', 'Laptop', 95000),
(7, 'Rahul', 'North', '2026-06-04', 'Mobile', 50000),
(8, 'Sneha', 'South', '2026-06-04', 'Tablet', 35000),
(9, 'Karan', 'West', '2026-06-05', 'Laptop', 95000),
(10, 'Neha', 'South', '2026-06-05', 'Mobile', 58000),
(11, 'Amit', 'North', '2026-06-06', 'Laptop', 100000),
(12, 'Priya', 'West', '2026-06-06', 'Tablet', 40000),
(13, 'Rahul', 'North', '2026-06-07', 'Laptop', 75000),
(14, 'Sneha', 'South', '2026-06-07', 'Mobile', 62000),
(15, 'Karan', 'West', '2026-06-08', 'Mobile', 58000),
(16, 'Neha', 'South', '2026-06-08', 'Laptop', 90000),
(17, 'Amit', 'North', '2026-06-09', 'Tablet', 45000),
(18, 'Priya', 'West', '2026-06-09', 'Mobile', 70000),
(19, 'Karan', 'West', '2026-06-10', 'Tablet', 38000),
(20, 'Neha', 'South', '2026-06-10', 'Tablet', 42000);

select * from sales_orders;
-- SUM
-- For each region level we will get total sum
select
	*,
    sum(order_amount) over(partition by region) as total_order_amount
from sales_orders;

-- Running SUM in each region

SELECT 
    *,
    SUM(order_amount) OVER(PARTITION BY region ORDER BY order_date) as region_level_amount
FROM sales_orders;

-- Running sum 
select
	*,
	SUM(order_amount) OVER(order by order_date) as running_total_amount
from sales_orders;

-- Ranking Function
-- Find the highest-value order from each region, If two orders have the same order_amount, 
-- pick the one with the latest order_date. If there is still a tie, pick the higher order_id.
select *
from (
	select 
		*,
		ROW_NUMBER() OVER(partition by region order by order_amount desc, order_date desc, order_id desc) as rnk
	from sales_orders
) rnk_region
where rnk_region.rnk = 1;

-- rank and dense rank
SELECT
    region,
    order_id,
    sales_rep,
    order_amount,

    RANK() OVER (
        PARTITION BY region
        ORDER BY order_amount DESC
    ) AS rank_position,

    DENSE_RANK() OVER (
        PARTITION BY region
        ORDER BY order_amount DESC
    ) AS dense_rank_position

FROM sales_orders
ORDER BY region, order_amount DESC, order_id;

-- LAG
CREATE TABLE product_monthly_revenue (
    revenue_id INT PRIMARY KEY,
    product_id INT,
    product_name VARCHAR(100),
    revenue_month DATE,
    revenue DECIMAL(10,2)
);

INSERT INTO product_monthly_revenue
(revenue_id, product_id, product_name, revenue_month, revenue)
VALUES
(1, 101, 'Wireless Mouse', '2026-01-01', 120000),
(2, 101, 'Wireless Mouse', '2026-02-01', 150000),
(3, 101, 'Wireless Mouse', '2026-03-01', 135000),
(4, 101, 'Wireless Mouse', '2026-04-01', 180000),
(5, 102, 'Mechanical Keyboard', '2026-01-01', 200000),
(6, 102, 'Mechanical Keyboard', '2026-02-01', 220000),
(7, 102, 'Mechanical Keyboard', '2026-03-01', 260000),
(8, 102, 'Mechanical Keyboard', '2026-04-01', 240000),
(9, 103, 'Laptop Stand', '2026-01-01', 90000),
(10, 103, 'Laptop Stand', '2026-02-01', 95000),
(11, 103, 'Laptop Stand', '2026-03-01', 130000),
(12, 103, 'Laptop Stand', '2026-04-01', 170000);

-- The product team wants to identify products whose revenue is declining. 
-- A product should be flagged if its revenue dropped compared to the previous month.
select 
	*,
	CASE
		WHEN prev_month_revenue = 0 THEN 'First Month'
        WHEN curr_month_revenue > prev_month_revenue Then 'Growth'
        WHEN curr_month_revenue < prev_month_revenue Then 'Drop'
        ELSE 'No Change'
    END as performance_revenue
FROM
	(select 
	revenue_id, 
    product_id,
    product_name,
    revenue_month, 
    revenue as curr_month_revenue,
	lag(revenue,1,0) over(partition by product_id order by revenue_month) as prev_month_revenue
from product_monthly_revenue) flaged_revenue;

-- LEAD
CREATE TABLE user_logins (
    login_id INT PRIMARY KEY,
    user_id INT,
    user_name VARCHAR(100),
    login_date DATE
);

INSERT INTO user_logins
(login_id, user_id, user_name, login_date)
VALUES
(1, 201, 'Amit', '2026-06-01'),
(2, 201, 'Amit', '2026-06-03'),
(3, 201, 'Amit', '2026-06-15'),
(4, 201, 'Amit', '2026-06-18'),
(5, 202, 'Priya', '2026-06-01'),
(6, 202, 'Priya', '2026-06-05'),
(7, 202, 'Priya', '2026-06-09'),
(8, 203, 'Rahul', '2026-06-02'),
(9, 203, 'Rahul', '2026-06-12'),
(10, 203, 'Rahul', '2026-06-25'),
(11, 204, 'Sneha', '2026-06-04'),
(12, 204, 'Sneha', '2026-06-06');
select * from user_logins;

-- The growth team wants to detect possible churn risk. A user is considered at risk if, 
-- after one login, their next login happens after more than 7 days

select 
	*,
    CASE
		WHEN next_login_date = 0 THEN 'Current_login'
        WHEN DATEDIFF(next_login_date, current_login_date) > 7 THEN 'Potential Risk'
        ELSE 'Normal'
    END as possible_risk
FROM (
	select 
		login_id,
		user_id, 
		user_name, 
		login_date as current_login_date,
		LEAD(login_date, 1, 0) OVER(PARTITION BY user_id Order By login_date) as next_login_date
	from user_logins
) risk_condition;

-- FRAME Clause
-- Rows Between
CREATE TABLE daily_stock_prices (
    price_id INT PRIMARY KEY,
    stock_symbol VARCHAR(20),
    price_date DATE,
    closing_price DECIMAL(10,2)
);

INSERT INTO daily_stock_prices
(price_id, stock_symbol, price_date, closing_price)
VALUES
(1, 'TCS', '2026-06-01', 3800),
(2, 'TCS', '2026-06-02', 3850),
(3, 'TCS', '2026-06-03', 3820),
(4, 'TCS', '2026-06-04', 3900),
(5, 'TCS', '2026-06-05', 3950),
(6, 'TCS', '2026-06-06', 3920),
(7, 'TCS', '2026-06-07', 4000),

(8, 'INFY', '2026-06-01', 1500),
(9, 'INFY', '2026-06-02', 1520),
(10, 'INFY', '2026-06-03', 1510),
(11, 'INFY', '2026-06-04', 1540),
(12, 'INFY', '2026-06-05', 1560),
(13, 'INFY', '2026-06-06', 1550),
(14, 'INFY', '2026-06-07', 1580);

select * from daily_stock_prices;

-- For each stock, calculate cumulative closing price day by day.
select
	*,
    SUM(closing_price) OVER( 
								partition by stock_symbol 
                                order by price_date rows between unbounded preceding and current row
							) as cumm_closing_price_as_of_now
from daily_stock_prices;

-- Calculate a 3-day moving average closing price for each stock.
select
	*,
    round(avg(closing_price) OVER( 
								partition by stock_symbol 
                                order by price_date rows between 2 preceding and current row
							), 2) as avg_closing_price
from daily_stock_prices;

-- Calculate the average closing price for the current day and next 2 trading days.
select
	*,
    round(avg(closing_price) OVER( 
								partition by stock_symbol 
                                order by price_date rows between current row and 2 following
							), 2) as 3_next_days_avg_closing_price
from daily_stock_prices;

-- Calculate a centered 3-day average: previous day, current day, and next day.
select
	*,
    round(avg(closing_price) OVER( 
								partition by stock_symbol 
                                order by price_date rows between 1 preceding and 1 following
							), 2) as 3_days_avg_closing_price
from daily_stock_prices;

-- These two queries will retrun same result, region level total sum for each row
-- 1)
select 
   *,
   sum(closing_price) over(partition by stock_symbol) as stock_level_sum
from daily_stock_prices;
-- 2)
select 
   *,
   sum(closing_price) over(partition by stock_symbol 
   order by price_date rows between unbounded preceding and unbounded following) as total_sum
from daily_stock_prices;

-- Range Between
CREATE TABLE daily_sales (
    sale_id INT PRIMARY KEY,
    sales_date DATE,
    sales_amount DECIMAL(10,2)
);

INSERT INTO daily_sales
(sale_id, sales_date, sales_amount)
VALUES
(1, '2026-06-01', 1000),
(2, '2026-06-02', 1500),
(3, '2026-06-03', 1200),
(4, '2026-06-05', 2000),
(5, '2026-06-06', 1800),
(6, '2026-06-10', 2500),
(7, '2026-06-11', 2200),
(8, '2026-06-12', 1700),
(9, '2026-06-15', 3000),
(10, '2026-06-16', 2800);

select 
   *,
   sum(sales_amount) over(order by sales_amount 
                    range between 300 preceding and 200 following) as total_sum
from daily_sales;

-- Find weekly running sum
select
	*,
	SUM(sales_amount) over(order by sales_date range between interval '6' day preceding and current row) as weekly_revenue
from daily_sales;

-- ========================================================
-- Iterative CTE
-- ========================================================

CREATE TABLE employees_new (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100),
    department VARCHAR(50),
    salary INT,
    performance_rating INT
);

INSERT INTO employees_new
(employee_id, employee_name, department, salary, performance_rating)
VALUES
(1, 'Amit', 'Engineering', 95000, 5),
(2, 'Priya', 'Engineering', 85000, 4),
(3, 'Rahul', 'Engineering', 70000, 3),
(4, 'Sneha', 'Engineering', 60000, 2),
(5, 'Karan', 'Data', 105000, 5),
(6, 'Neha', 'Data', 92000, 4),
(7, 'Rohit', 'Data', 76000, 3),
(8, 'Anjali', 'Data', 68000, 2),
(9, 'Vikas', 'Sales', 80000, 5),
(10, 'Pooja', 'Sales', 72000, 4),
(11, 'Nikhil', 'Sales', 62000, 3),
(12, 'Simran', 'Sales', 55000, 2);

select * from employees_new;

-- Find employees whose salary is greater than the average salary of their department.

with avg_dept_salary_cte as (
	select 
		department,
        avg(salary) as avg_salary
	from employees_new
    group by department
)
select
	employees_new.employee_id,
    employees_new.employee_name,
    employees_new.department,
    employees_new.salary,
    avg_dept_salary_cte.avg_salary
from employees_new
inner join avg_dept_salary_cte
on employees_new.department = avg_dept_salary_cte.department 
and employees_new.salary > avg_dept_salary_cte.avg_salary;

