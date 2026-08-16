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
