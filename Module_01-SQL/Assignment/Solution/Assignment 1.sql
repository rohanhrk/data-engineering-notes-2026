CREATE DATABASE db_assignment_1;

use db_assignment_1;

-- ================================================================================
-- QUESTION 1: Employee Salary Ranking by Department
-- ================================================================================
-- problem statement : Find the rank of each employee's salary within their department. Include employees 
-- who have the same salary (they should get the same rank).
CREATE TABLE emp_salary (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO emp_salary VALUES
(1, 'Alice', 'Engineering', 75000),
(2, 'Bob', 'Engineering', 80000),
(3, 'Charlie', 'Engineering', 75000),
(4, 'Diana', 'Sales', 60000),
(5, 'Eve', 'Sales', 65000),
(6, 'Frank', 'Sales', 60000);

select 
	*,
    RANK() OVER(PARTITION BY department ORDER BY salary DESC) as rnk
from emp_salary;

-- ================================================================================
-- QUESTION 2: Running Total of Daily Sales
-- ================================================================================
-- Problem Statement:
-- Calculate the running total of sales amount for each day, ordered by date.

CREATE TABLE daily_sales (
    sale_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO daily_sales VALUES
('2024-01-01', 1000),
('2024-01-02', 1500),
('2024-01-03', 800),
('2024-01-04', 2000),
('2024-01-05', 1200);


select 
	*,
    SUM(amount) OVER(ORDER BY sale_date) as running_revenue
from daily_sales;

-- ================================================================================
-- QUESTION 3: Top 3 Products by Revenue Per Category
-- ================================================================================

-- Problem Statement:
-- Find the top 3 products by revenue in each category. If there are ties, include all 
-- tied products.

CREATE TABLE product_revenue (
    product_id INT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    revenue DECIMAL(10,2)
);

INSERT INTO product_revenue VALUES
(1, 'Laptop', 'Electronics', 50000),
(2, 'Phone', 'Electronics', 45000),
(3, 'Tablet', 'Electronics', 30000),
(4, 'Headphones', 'Electronics', 15000),
(5, 'Chair', 'Furniture', 8000),
(6, 'Desk', 'Furniture', 12000),
(7, 'Sofa', 'Furniture', 20000),
(8, 'Lamp', 'Furniture', 3000);

with dense_rank_category_cte as (
	select 
		*,
		dense_rank() over(partition by category order by revenue desc) as rnk
	from product_revenue
)
select *
from dense_rank_category_cte
where rnk <= 3;

-- ================================================================================
-- QUESTION 4: Previous and Next Order Amount
-- ================================================================================

-- Problem Statement:
-- For each order, show the previous order amount and next order amount for the same 
-- customer.

CREATE TABLE customer_orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO customer_orders VALUES
(1, 101, '2024-01-10', 500),
(2, 101, '2024-01-15', 750),
(3, 101, '2024-01-20', 600),
(4, 102, '2024-01-12', 300),
(5, 102, '2024-01-18', 450);

select 
	order_id,
    customer_id,
    order_date,
    amount as current_amount,
    lag(amount) over(partition by customer_id order by order_date) as prev_amount,
    lead(amount) over(partition by customer_id order by order_date) as next_amount
from customer_orders;

-- ================================================================================
-- QUESTION 5: Moving Average of Stock Prices (3-day window)
-- ================================================================================

-- Problem Statement:
-- Calculate the 3-day moving average of stock prices for each stock symbol.

CREATE TABLE stock_prices (
    symbol VARCHAR(10),
    trade_date DATE,
    closing_price DECIMAL(10,2)
);

INSERT INTO stock_prices VALUES
('AAPL', '2024-01-01', 150.00),
('AAPL', '2024-01-02', 152.50),
('AAPL', '2024-01-03', 151.00),
('AAPL', '2024-01-04', 155.00),
('AAPL', '2024-01-05', 153.50),
('GOOGL', '2024-01-01', 2800.00),
('GOOGL', '2024-01-02', 2850.00),
('GOOGL', '2024-01-03', 2820.00);

select 
	*,
    round(AVG(closing_price) 
	over(
			partition by symbol 
			order by trade_date rows between 2 preceding and current row
        ), 2) as moving_avg_3day
from stock_prices;

-- ================================================================================
-- QUESTION 6: Employees Earning More Than Department Average
-- ================================================================================

-- Problem Statement:
-- Find employees whose salary is greater than the average salary of their department.
-- Show the employee details along with department average.

CREATE TABLE employees (
    emp_id INT,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
(1, 'Alice', 'Engineering', 85000),
(2, 'Bob', 'Engineering', 75000),
(3, 'Charlie', 'Engineering', 90000),
(4, 'Diana', 'Sales', 55000),
(5, 'Eve', 'Sales', 70000),
(6, 'Frank', 'Sales', 50000);

select 
	e1.emp_id,
    e1.emp_name,
    e1.department,
    e1.salary,
    e2.avg_dept_salary
from employees e1
inner join(
	select
		department,
		round(avg(salary), 2) as avg_dept_salary
	from employees
	group by department
) e2
on e1.department = e2.department and e1.salary > e2.avg_dept_salary;

-- ================================================================================
-- QUESTION 7: Year-over-Year Sales Growth
-- ================================================================================

-- Problem Statement:
-- Calculate the year-over-year growth percentage for each product.

CREATE TABLE yearly_sales (
    product_id INT,
    product_name VARCHAR(100),
    year INT,
    total_sales DECIMAL(12,2)
);

INSERT INTO yearly_sales VALUES
(1, 'Widget A', 2022, 100000),
(1, 'Widget A', 2023, 120000),
(1, 'Widget A', 2024, 150000),
(2, 'Widget B', 2022, 80000),
(2, 'Widget B', 2023, 75000),
(2, 'Widget B', 2024, 90000);

with prev_total_sales_cte as (
	select 
		product_id,
		product_name,
		year,
		total_sales as current_total_sales,
		lag(total_sales) over(partition by product_name order by year) as previous_total_sales
	from yearly_sales
)
select 
	*, 
    round(((current_total_sales - previous_total_sales)/previous_total_sales) * 100, 2) as growth_percentage
from prev_total_sales_cte;

-- ================================================================================
-- QUESTION 8: First and Last Purchase Date Per Customer
-- ================================================================================

-- Problem Statement:
-- For each customer, find their first purchase date, last purchase date, and the 
-- number of days between them.

CREATE TABLE purchases (
    purchase_id INT,
    customer_id INT,
    purchase_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO purchases VALUES
(1, 101, '2024-01-05', 200),
(2, 101, '2024-02-15', 350),
(3, 101, '2024-03-20', 150),
(4, 102, '2024-01-10', 500),
(5, 102, '2024-01-25', 300),
(6, 103, '2024-02-01', 400);

select 
	customer_id,
    min(purchase_date) as first_purchase_date,
    max(purchase_date) as last_purchase_date,
    datediff(max(purchase_date), min(purchase_date)) as days_gap
from purchases
group by customer_id;

-- ================================================================================
-- QUESTION 9: Consecutive Login Streak
-- ================================================================================

-- Problem Statement:
-- Find users who have logged in for at least 3 consecutive days. Show the user and 
-- their maximum consecutive login streak.

CREATE TABLE user_logins (
    user_id INT,
    login_date DATE
);

INSERT INTO user_logins VALUES
(1, '2024-01-01'),
(1, '2024-01-02'),
(1, '2024-01-03'),
(1, '2024-01-04'),
(1, '2024-01-06'),
(2, '2024-01-01'),
(2, '2024-01-02'),
(2, '2024-01-05'),
(3, '2024-01-10'),
(3, '2024-01-11'),
(3, '2024-01-12');

select * from user_logins;

with unique_login_days_cte as (
	select distinct
		user_id,
        login_date
    from user_logins
), row_number_substract_cte as (
	select
		user_id,
        login_date,
        row_number() over(partition by user_id order by login_date) as rn,
        date_sub(login_date, interval row_number() over(partition by user_id order by login_date) day) as grp
    from unique_login_days_cte
), group_by_cte as (
	select
		user_id, 
        grp,
        count(*) as consecutive_login_days
    from row_number_substract_cte
    group by user_id, grp
)

select 
	user_id,
    max(consecutive_login_days) as max_streak
from group_by_cte
group by user_id
having max_streak >= 3;

-- ================================================================================
-- QUESTION 10: Percentage of Total Sales by Product
-- ================================================================================

-- Problem Statement:
-- Calculate what percentage each product contributes to the total sales.

CREATE TABLE product_sales (
    product_id INT,
    product_name VARCHAR(100),
    sales_amount DECIMAL(10,2)
);

INSERT INTO product_sales VALUES
(1, 'Product A', 5000),
(2, 'Product B', 3000),
(3, 'Product C', 2000),
(4, 'Product D', 10000);

select * from product_sales;


with total_sales_cte as (
	select sum(sales_amount) as total_sales
    from product_sales
)
select
	*,
    round((ps.sales_amount/ts.total_sales) * 100,2) as percentage_growth
from product_sales ps
join total_sales_cte ts;

-- ================================================================================
-- QUESTION 11: Row Number with Reset on Category Change
-- ================================================================================

-- Problem Statement:
-- Assign a sequential row number to each product within its category, ordered by 
-- product name.
drop table products;
CREATE TABLE products (
    product_id INT,
    product_name VARCHAR(100),
    category VARCHAR(50)
);

INSERT INTO products VALUES
(1, 'Apple', 'Fruits'),
(2, 'Banana', 'Fruits'),
(3, 'Cherry', 'Fruits'),
(4, 'Carrot', 'Vegetables'),
(5, 'Broccoli', 'Vegetables'),
(6, 'Milk', 'Dairy'),
(7, 'Cheese', 'Dairy');

select 
	*,
    ROW_NUMBER() OVER(partition by category order by product_name) as rn
from products;

-- ================================================================================
-- QUESTION 12: Cumulative Sum with Partition Reset
-- ================================================================================

-- Problem Statement:
-- Calculate cumulative sales for each salesperson, resetting the cumulative sum 
-- when the month changes.

CREATE TABLE sales_data (
    sale_id INT,
    salesperson VARCHAR(50),
    sale_month INT,
    sale_amount DECIMAL(10,2)
);

INSERT INTO sales_data VALUES
(1, 'John', 1, 1000),
(2, 'John', 1, 1500),
(3, 'John', 2, 2000),
(4, 'John', 2, 1000),
(5, 'Mary', 1, 800),
(6, 'Mary', 1, 1200),
(7, 'Mary', 2, 1500);

select
	*,
    SUM(sale_amount) OVER(partition by salesperson, sale_month order by sale_month ROWS BETWEEN unbounded preceding and current row) as cum_sales
from sales_data;

-- ================================================================================
-- QUESTION 13: Find Median Salary Per Department
-- ================================================================================

-- Problem Statement:
-- Calculate the median salary for each department.

CREATE TABLE dept_salaries (
    emp_id INT,
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO dept_salaries VALUES
(1, 'Engineering', 70000),
(2, 'Engineering', 80000),
(3, 'Engineering', 90000),
(4, 'Engineering', 85000),
(5, 'Sales', 50000),
(6, 'Sales', 60000),
(7, 'Sales', 55000);

with row_number_cte as (
	select 
		*,
		ROW_NUMBER() over(partition by department order by salary) as rn,
        count(*) over(partition by department) as total_count
	from dept_salaries
)
select
	department,
    round(avg(salary),2) as median
from row_number_cte
where rn in (
	(total_count + 1) / 2,
    (total_count + 2) / 2
)
group by department;

-- ================================================================================
-- QUESTION 14: Nth Highest Salary (Find 3rd Highest)
-- ================================================================================

-- Problem Statement:
-- Find employees with the 3rd highest salary in each department.

CREATE TABLE emp_salaries (
    emp_id INT,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO emp_salaries VALUES
(1, 'Alice', 'IT', 90000),
(2, 'Bob', 'IT', 85000),
(3, 'Charlie', 'IT', 80000),
(4, 'Diana', 'IT', 75000),
(5, 'Eve', 'HR', 70000),
(6, 'Frank', 'HR', 65000),
(7, 'Grace', 'HR', 60000),
(8, 'Henry', 'HR', 55000);

select * from emp_salaries;

with row_number_cte as (
	select
		*,
		ROW_NUMBER() OVER(partition by department order by salary desc) as rn
	from emp_salaries
)

select 
	emp_id,
    emp_name,
    department,
    salary as 3rd_highest_salary
from row_number_cte
where rn = 3;

-- ================================================================================
-- QUESTION 15: Identify Gaps in Sequential Data
-- ================================================================================

-- Problem Statement:
-- Find missing order IDs in a sequence of orders.

CREATE TABLE orders (
    order_id INT
);

INSERT INTO orders VALUES
(1), (2), (3), (5), (6), (8), (10);

select * from orders;

With recursive numbers as (
	-- 1. Anchor query
	select min(order_id) as num
    from orders
    UNION
    -- 2. Rcursion Query
    select num + 1
    from numbers
    where num < (select max(order_id) as num from orders)
)
select 
	num as missing_id
from numbers n
where num not in (
	select 
		order_id
	from orders o
);

-- ================================================================================
-- QUESTION 16: Dense Rank vs Rank Comparison
-- ================================================================================

-- Problem Statement:
-- Show both RANK and DENSE_RANK for student scores and explain the difference 
-- through results.

CREATE TABLE student_scores (
    student_id INT,
    student_name VARCHAR(100),
    score INT
);

INSERT INTO student_scores VALUES
(1, 'Alice', 95),
(2, 'Bob', 90),
(3, 'Charlie', 90),
(4, 'Diana', 85),
(5, 'Eve', 80);

select 
	*,
    RANK() over(order by score desc) as rnk,
    dense_rank() over(order by score desc) as den_rnk
from student_scores;

-- ================================================================================
-- QUESTION 17: First Value and Last Value in Window
-- ================================================================================

-- Problem Statement:
-- For each transaction, show the first and last transaction amount for that customer.
CREATE TABLE transactions (
    txn_id INT,
    customer_id INT,
    txn_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO transactions VALUES
(1, 101, '2024-01-01', 100),
(2, 101, '2024-01-05', 200),
(3, 101, '2024-01-10', 150),
(4, 102, '2024-01-02', 300),
(5, 102, '2024-01-08', 250);


with first_last_txn_date_cte as (
	select
		customer_id,
		min(txn_date) as first_txn_date,
		max(txn_date) as last_txn_date
	from transactions
	group by customer_id
), first_txn_amount as (
	select 
		tr.customer_id,
        tr.amount as first_txn_amount
	from transactions tr
    inner join first_last_txn_date_cte flt
    on tr.customer_id = flt.customer_id and tr.txn_date = flt.first_txn_date
), last_txn_amount as (
	select 
		tr.customer_id,
		tr.amount as last_txn_amount
	from transactions tr
	inner join first_last_txn_date_cte flt
	on tr.customer_id = flt.customer_id and tr.txn_date = flt.last_txn_date
)

select 
	tr.*,
    ft.first_txn_amount,
    lt.last_txn_amount
from transactions tr
inner join first_txn_amount ft
inner join last_txn_amount lt
on tr.customer_id = ft.customer_id and ft.customer_id = lt.customer_id;

-- ================================================================================
-- QUESTION 18: Hierarchical Employee Manager Query
-- ================================================================================

-- Problem Statement:
-- Using a recursive CTE, find all employees and their manager chain up to the CEO.

CREATE TABLE emp_hierarchy (
    emp_id INT,
    emp_name VARCHAR(100),
    manager_id INT
);

ALTER TABLE emp_hierarchy modify column emp_name varchar(300);

INSERT INTO emp_hierarchy VALUES
(1, 'CEO', NULL),
(2, 'VP Sales', 1),
(3, 'VP Engineering', 1),
(4, 'Sales Manager', 2),
(5, 'Engineer Lead', 3),
(6, 'Sales Rep', 4),
(7, 'Developer', 5);
select * from emp_hierarchy;
with recursive emp_hierarcies_tree_cte as (
	select 
		emp_id,
        emp_name,
        1 as level,
        CAST('CEO' AS CHAR(1000)) as hierarchy_path
	from emp_hierarchy
    where manager_id is NULL
    UNION ALL
    select
		emh.emp_id,
        emh.emp_name,
        emht.level + 1,
		concat(hierarchy_path, "->", emh.emp_name)
	from emp_hierarchy emh
    inner join emp_hierarcies_tree_cte emht
    on emht.emp_id = emh.manager_id
)
select * from emp_hierarcies_tree_cte;

-- ================================================================================
-- QUESTION 19: Difference from Previous Row
-- ================================================================================

-- Problem Statement:
-- Calculate the difference in temperature from the previous day for each city.

CREATE TABLE weather (
    city VARCHAR(50),
    record_date DATE,
    temperature DECIMAL(5,2)
);

INSERT INTO weather VALUES
('NYC', '2024-01-01', 32.5),
('NYC', '2024-01-02', 35.0),
('NYC', '2024-01-03', 28.5),
('LA', '2024-01-01', 65.0),
('LA', '2024-01-02', 68.5),
('LA', '2024-01-03', 70.0);

select
	city,
    record_date,
    temperature as current_temp,
    temperature - lag(temperature) over(partition by city order by record_date) as temp_change
from weather;

-- ================================================================================
-- QUESTION 20:  Divide Data into Quartiles
-- ================================================================================
-- Problem Statement:
-- Divide employees into 4 salary quartiles within their department.

CREATE TABLE emp_quartiles (
    emp_id INT,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO emp_quartiles VALUES
(1, 'A', 'IT', 90000),
(2, 'B', 'IT', 85000),
(3, 'C', 'IT', 80000),
(4, 'D', 'IT', 75000),
(5, 'E', 'IT', 70000),
(6, 'F', 'IT', 65000),
(7, 'G', 'IT', 60000),
(8, 'H', 'IT', 55000);

select 
	*,
    CASE
		WHEN emp_id % 2 = 0 THEN emp_id / 2
        ELSE round(ceil(emp_id / 2), 1)
    END as quartiles
from emp_quartiles;

-- OR using NTILE

select 
	*,
    NTILE(4) over(partition by department order by salary desc) as quartiles
from emp_quartiles;


-- ================================================================================
-- QUESTION 21: Pivot Monthly Sales Data
-- ================================================================================

-- Problem Statement:
-- Transform monthly sales data from rows to columns (pivot).


CREATE TABLE monthly_sales (
    product VARCHAR(50),
    month VARCHAR(20),
    sales DECIMAL(10,2)
);

INSERT INTO monthly_sales VALUES
('Product A', 'January', 1000),
('Product A', 'February', 1200),
('Product A', 'March', 1100),
('Product B', 'January', 800),
('Product B', 'February', 900),
('Product B', 'March', 950);

select 
	product,
    cast(sum(CASE WHEN month = 'January' THEN sales ELSE 0 END) as signed) as January,
    cast(sum(CASE WHEN month = 'February' THEN sales ELSE 0 END) as signed) as February,
    cast(sum(CASE WHEN month = 'March' THEN sales ELSE 0 END) as signed) as March
from monthly_sales
group by product;

-- ================================================================================
-- QUESTION 22: Find Duplicate Records
-- ================================================================================

-- Problem Statement:
-- Find all customers who have duplicate email addresses.
drop table customers;
CREATE TABLE customers (
    customer_id INT,
    customer_name VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO customers VALUES
(1, 'Alice', 'alice@email.com'),
(2, 'Bob', 'bob@email.com'),
(3, 'Charlie', 'alice@email.com'),
(4, 'Diana', 'diana@email.com'),
(5, 'Eve', 'bob@email.com');

select 
	c1.* 
from customers c1
inner join customers c2
on c1.email = c2.email and c1.customer_id != c2.customer_id
order by c1.email, c1.customer_id;

-- or 

With dublicate_email_record_cte as (
	Select
		email,
		count(*) as number_of_record
	from customers
	group by email
)
Select 
	c2.*
from dublicate_email_record_cte c1
inner join customers c2
on c1.email = c2.email and c1.number_of_record > 1
order by email, customer_id;

-- ================================================================================
-- QUESTION 23: Calculate Time Between Events
-- ================================================================================

-- Problem Statement:
-- Calculate the time difference between consecutive page views for each user.

CREATE TABLE page_views (
    view_id INT,
    user_id INT,
    page_name VARCHAR(100),
    view_time TIMESTAMP
);

INSERT INTO page_views VALUES
(1, 101, 'Home', '2024-01-01 10:00:00'),
(2, 101, 'Products', '2024-01-01 10:05:00'),
(3, 101, 'Cart', '2024-01-01 10:12:00'),
(4, 102, 'Home', '2024-01-01 11:00:00'),
(5, 102, 'Products', '2024-01-01 11:03:00');

WITH next_page_view as (
	select 
		*,
		LEAD(view_time) over(partition by user_id order by view_time) as next_view_time
	from page_views
)

select
	user_id,
    page_name,
    view_time,
	minute(timediff(next_view_time, view_time)) as time_on_page_mins 
from next_page_view;

-- ================================================================================
-- QUESTION 24: Find Employees with Same Salary
-- ================================================================================

-- Problem Statement:
-- Find pairs of employees who have the same salary.

CREATE TABLE emp_pairs (
    emp_id INT,
    emp_name VARCHAR(100),
    salary DECIMAL(10,2)
);

INSERT INTO emp_pairs VALUES
(1, 'Alice', 75000),
(2, 'Bob', 80000),
(3, 'Charlie', 75000),
(4, 'Diana', 85000),
(5, 'Eve', 80000);


with windowed_cte as (
	select
		*,
		COUNT(*) over(partition by salary) as count_record_per_partition,
		row_number() over(partition by salary) as rn
	from emp_pairs
), first_employee_cte as (
	Select
		emp_name as employee_1,
		salary
	From windowed_cte
	where count_record_per_partition = 2 and rn = 1
), second_employee_cte as (
	Select
		emp_name as employee_2,
		salary
	From windowed_cte
	where count_record_per_partition = 2 and rn = 2
)

select
	fe.employee_1,
    se.employee_2,
    CAST(se.salary as signed) as salary
from first_employee_cte fe
inner join second_employee_cte se
on fe.salary = se.salary;

-- ================================================================================
-- QUESTION 25: Rolling Sum (Last 3 Days)
-- ================================================================================

-- Problem Statement:
-- Calculate a rolling sum of orders for the last 3 days for each store.

CREATE TABLE store_orders (
    store_id INT,
    order_date DATE,
    order_count INT
);

INSERT INTO store_orders VALUES
(1, '2024-01-01', 10),
(1, '2024-01-02', 15),
(1, '2024-01-03', 12),
(1, '2024-01-04', 18),
(1, '2024-01-05', 20),
(2, '2024-01-01', 8),
(2, '2024-01-02', 10),
(2, '2024-01-03', 9);

select
	*,
    SUM(order_count) over(partition by store_id order by order_date rows between 2 preceding and current row) as last_3_days_order
from store_orders;

-- ================================================================================
-- QUESTION 26: Count Distinct in Window
-- ================================================================================

-- Problem Statement:
-- For each order, show how many distinct products have been ordered by that 
-- customer up to and including that order.

CREATE TABLE cust_orders (
    order_id INT,
    customer_id INT,
    product_id INT,
    order_date DATE
);
drop table cust_orders;
INSERT INTO cust_orders VALUES
(1, 101, 1, '2024-01-01'),
(2, 101, 2, '2024-01-02'),
(3, 101, 1, '2024-01-03'),
(4, 101, 3, '2024-01-04'),
(5, 102, 1, '2024-01-01'),
(6, 102, 1, '2024-01-02');

WITH first_purchase AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id, product_id
            ORDER BY order_date
        ) AS rn
    FROM cust_orders
)
SELECT
    *,
    SUM(CASE WHEN rn = 1 THEN 1 ELSE 0 END)
        OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS distinct_product_so_far
FROM first_purchase;


-- ================================================================================
-- QUESTION 27: Islands and Gaps Problem
-- ================================================================================

-- Problem Statement:
-- Identify continuous periods (islands) when a server was active.

CREATE TABLE server_status (
    status_date DATE,
    is_active INT -- 1 for active, 0 for inactive
);

INSERT INTO server_status VALUES
('2024-01-01', 1),
('2024-01-02', 1),
('2024-01-03', 1),
('2024-01-04', 0),
('2024-01-05', 0),
('2024-01-06', 1),
('2024-01-07', 1),
('2024-01-08', 0),
('2024-01-09', 1);

with running_sum as (
	select 
		*,
		sum(CASE WHEN is_active = 1 THEN 0 ELSE 1 END) over(order by status_date) as rank_sum
	from server_status
)
select
	min(status_date) as period_start,
    max(status_date) as period_end,
    count(*) as days_active
from running_sum
group by is_active, rank_sum
having is_active = 1;


-- ================================================================================
-- QUESTION 28: Percent Rank and Cumulative Distribution
-- ================================================================================

-- Problem Statement:
-- Calculate PERCENT_RANK and CUME_DIST for employee salaries.

CREATE TABLE emp_dist (
    emp_id INT,
    emp_name VARCHAR(100),
    salary DECIMAL(10,2)
);

INSERT INTO emp_dist VALUES
(1, 'Alice', 50000),
(2, 'Bob', 60000),
(3, 'Charlie', 70000),
(4, 'Diana', 80000),
(5, 'Eve', 90000);

select 
	*,
    percent_rank() over(order by salary) as pr,
    cume_dist() over(order by salary) as cd
from emp_dist;

-- ================================================================================
-- QUESTION 29:
-- ================================================================================

-- Problem Statement:
-- Demonstrate the difference between ROWS and RANGE by calculating sum of 
-- amounts where there are duplicate values.

CREATE TABLE frame_demo (
    id INT,
    category VARCHAR(20),
    value INT
);

INSERT INTO frame_demo VALUES
(1, 'A', 10),
(2, 'A', 20),
(3, 'A', 20),
(4, 'A', 30),
(5, 'A', 40);

select
	*,
    SUM(VALUE) OVER(ORDER BY value rows between unbounded preceding and current row) as rows_running_sum,
	SUM(VALUE) OVER(ORDER BY value range between unbounded preceding and current row) as range_running_sum
from frame_demo;

-- ================================================================================
-- QUESTION 30:
-- ================================================================================
-- Problem Statement:
-- Find the top spending customer in each month, along with their total spend and 
-- the percentage of total monthly sales they represent.

CREATE TABLE sales_transactions (
    txn_id INT,
    customer_id INT,
    txn_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO sales_transactions VALUES
(1, 101, '2024-01-05', 500),
(2, 101, '2024-01-15', 300),
(3, 102, '2024-01-10', 600),
(4, 103, '2024-01-20', 200),
(5, 101, '2024-02-05', 400),
(6, 102, '2024-02-10', 700),
(7, 102, '2024-02-15', 300),
(8, 103, '2024-02-20', 500);

WITH customers_monthy_orders as (
	select 
		date_format(txn_date, '%Y-%m') as trxn_month,
		customer_id,
		sum(amount) as monthly_total_orders_by_each_customer
	from sales_transactions
	group by trxn_month, customer_id
), monthly_order_contribution_by_each_customer as (
	select
		*,
        sum(monthly_total_orders_by_each_customer) over(partition by trxn_month) as monthly_sales,
        rank() over(partition by trxn_month order by monthly_total_orders_by_each_customer desc) as rnk
	from customers_monthy_orders
)
Select 
	*,
	round((monthly_total_orders_by_each_customer / monthly_sales) * 100, 2) as percentage_of_monthly
from monthly_order_contribution_by_each_customer
WHERE rnk = 1;