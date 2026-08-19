CREATE database assignment_sql;
USE assignment_sql;
-- ================================================================================
-- QUESTION 1: Products Never Ordered
-- ================================================================================

-- Problem Statement:
-- Find all products that have never been ordered.

CREATE TABLE assignment_sql.products_q1 (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE assignment_sql.order_items_q1 (
    order_id INT,
    product_id INT,
    quantity INT
);


INSERT INTO assignment_sql.products_q1 VALUES
(1, 'Laptop', 1000),
(2, 'Mouse', 25),
(3, 'Keyboard', 75),
(4, 'Monitor', 300),
(5, 'Webcam', 50);

INSERT INTO assignment_sql.order_items_q1 VALUES
(1, 1, 2),
(1, 2, 3),
(2, 1, 1),
(3, 3, 2);

SELECT * FROM products_q1;
SELECT * FROM order_items_q1;

SELECT *
FROM products_q1 p
WHERE NOT exists (
	SELECT
		1
	FROM order_items_q1 o
    WHERE p.product_id = o.product_id
);

-- ================================================================================
-- QUESTION 2: Customers with Orders Above Average
-- ================================================================================

-- Problem Statement:
-- Find customers whose total order amount is above the average total order amount 
-- across all customers.

CREATE TABLE assignment_sql.customers_q2 (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE assignment_sql.orders_q2 (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.customers_q2 VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie'),
(4, 'Diana');

INSERT INTO assignment_sql.orders_q2 VALUES
(1, 1, 500),
(2, 1, 300),
(3, 2, 150),
(4, 3, 800),
(5, 3, 400),
(6, 4, 200);

SELECT * FROM customers_q2;
SELECT * FROM orders_q2;

WITH total_sales_cte as (
	SELECT 
		AVG(order_amount) as avg_sales
	FROM orders_q2
), total_sales_by_each_customer_cte as (
	SELECT
		customer_id,
        SUM(order_amount) as total_sales
    FROM orders_q2
    GROUP BY customer_id
), validated_customer_cte as (
	SELECT *
    FROM total_sales_by_each_customer_cte c
    WHERE c.total_sales > (
		SELECT avg_sales
        FROM total_sales_cte
    )
)
SELECT c.customer_name, vc.total_sales
FROM customers_q2 c
INNER JOIN validated_customer_cte vc
ON c.customer_id = vc.customer_id;

-- ================================================================================
-- QUESTION 3: Employees with Manager's Salary
-- ================================================================================

-- Problem Statement:
-- Find employees who earn more than their manager.

CREATE TABLE assignment_sql.emp_mgr (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    manager_id INT,
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.emp_mgr VALUES
(1, 'CEO', NULL, 150000),
(2, 'Manager A', 1, 90000),
(3, 'Manager B', 1, 85000),
(4, 'Employee X', 2, 95000),
(5, 'Employee Y', 2, 70000),
(6, 'Employee Z', 3, 80000);

select * from emp_mgr;

select
	e.emp_name,
    e.salary,
    m.emp_name,
    m.salary
from emp_mgr e
inner join emp_mgr m
on e.manager_id = m.emp_id
and e.salary > m.salary;


-- ================================================================================
-- QUESTION 4: Department with Highest Average Salary
-- ================================================================================

-- Problem Statement:
-- Find the department with the highest average salary.

CREATE TABLE assignment_sql.dept_emp (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.dept_emp VALUES
(1, 'Alice', 'Engineering', 90000),
(2, 'Bob', 'Engineering', 85000),
(3, 'Charlie', 'Sales', 60000),
(4, 'Diana', 'Sales', 65000),
(5, 'Eve', 'HR', 55000),
(6, 'Frank', 'HR', 50000);

WITH windowed_cte as (
	select
		department,
		avg_department_salary,
		rank() over(order by avg_department_salary desc) as rnk
	from (
		select 
			department, 
			round(avg(salary), 2) as avg_department_salary
		from dept_emp
		group by department
	) avg_dept_salary
)
SELECT 
	department,
    avg_department_salary as avg_salary
FROM windowed_cte
WHERE rnk = 1;

-- ================================================================================
-- QUESTION 5: Latest Order Per Customer
-- ================================================================================

-- Problem Statement:
-- Find the latest order for each customer using a correlated subquery.

CREATE TABLE assignment_sql.cust_orders_q5 (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.cust_orders_q5 VALUES
(1, 101, '2024-01-10', 500),
(2, 101, '2024-01-20', 300),
(3, 101, '2024-02-05', 450),
(4, 102, '2024-01-15', 600),
(5, 102, '2024-01-25', 350),
(6, 103, '2024-02-01', 400);

SELECT
	*
FROM cust_orders_q5 oc
WHERE oc.order_date > ALL (
	SELECT 
		order_date
	FROM cust_orders_q5 ic
    WHERE oc.customer_id = ic.customer_id and oc.order_date <> ic.order_date
);


-- ================================================================================
-- QUESTION 6: Complete Sales Analysis
-- ================================================================================

-- Problem Statement:
-- Show all products and all orders, including products with no orders and orders 
-- with invalid product references.

CREATE TABLE assignment_sql.products_q6 (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100)
);

CREATE TABLE assignment_sql.sales_q6 (
    sale_id INT PRIMARY KEY,
    product_id INT,
    quantity INT
);

INSERT INTO assignment_sql.products_q6 VALUES
(1, 'Product A'),
(2, 'Product B'),
(3, 'Product C');

INSERT INTO assignment_sql.sales_q6 VALUES
(1, 1, 10),
(2, 1, 5),
(3, 2, 8),
(4, 4, 3);  -- product_id 4 doesn't exist

select * from assignment_sql.products_q6;
select * from assignment_sql.sales_q6;

select 
	p.*,
    s.sale_id,
    s.quantity
from assignment_sql.products_q6 p
left JOIN assignment_sql.sales_q6 s
on p.product_id = s.product_id
UNION ALL
select 
	s.product_id,
    NULL as product_name,
    s.sale_id,
    s.quantity
from assignment_sql.products_q6 p
right JOIN assignment_sql.sales_q6 s
on p.product_id = s.product_id
where p.product_id IS NULL;

-- ================================================================================
-- QUESTION 7: Find Active Customers
-- ================================================================================

-- Problem Statement:
-- Find customers who have placed at least one order in the last 30 days using 
-- both EXISTS and IN (show both solutions).

CREATE TABLE assignment_sql.customers_q7 (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE assignment_sql.orders_q7 (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE
);

INSERT INTO assignment_sql.customers_q7 VALUES
(1, 'Alice', 'alice@email.com'),
(2, 'Bob', 'bob@email.com'),
(3, 'Charlie', 'charlie@email.com'),
(4, 'Diana', 'diana@email.com');

INSERT INTO assignment_sql.orders_q7 VALUES
(1, 1, '2024-01-25'),
(2, 1, '2024-01-10'),
(3, 2, '2023-12-15'),
(4, 3, '2024-01-28');

-- Assume current date is 2024-01-30

select * from assignment_sql.customers_q7;
select * from assignment_sql.orders_q7;


SELECT 
	c.*
FROM assignment_sql.customers_q7 c
WHERE EXISTS (
	SELECT 
		1
	FROM assignment_sql.orders_q7 o
    WHERE c.customer_id = o.customer_id AND o.order_date BETWEEN date_sub("2024-01-30", interval 30 day) AND "2024-01-30"
);

SELECT 
c.*
FROM assignment_sql.customers_q7 c
WHERE c.customer_id IN (
	SELECT o.customer_id
    FROM assignment_sql.orders_q7 o
    WHERE o.order_date BETWEEN date_sub("2024-01-30", interval 30 day) AND "2024-01-30"
);

-- ================================================================================
-- QUESTION 8: 
-- ================================================================================

-- Problem Statement:
-- Find total sales amount for each product category.

CREATE TABLE assignment_sql.categories_q8 (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(50)
);

CREATE TABLE assignment_sql.products_q8 (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category_id INT,
    price DECIMAL(10,2)
);

CREATE TABLE assignment_sql.order_items_q8 (
    order_id INT,
    product_id INT,
    quantity INT
);

INSERT INTO assignment_sql.categories_q8 VALUES
(1, 'Electronics'),
(2, 'Clothing'),
(3, 'Books');

INSERT INTO assignment_sql.products_q8 VALUES
(1, 'Laptop', 1, 1000),
(2, 'Phone', 1, 500),
(3, 'T-Shirt', 2, 25),
(4, 'Jeans', 2, 50),
(5, 'Novel', 3, 15);

INSERT INTO assignment_sql.order_items_q8 VALUES
(1, 1, 2),
(1, 3, 5),
(2, 2, 3),
(2, 4, 2),
(3, 1, 1),
(3, 5, 4);

select * from assignment_sql.categories_q8;	
select * from assignment_sql.products_q8;		
select * from assignment_sql.order_items_q8;

WITH product_total_sales_cte as (
	SELECT 
		p.product_id,
        p.product_name,
        p.category_id,
        p.price,
        o.order_id,
        o.quantity,
        p.price * o.quantity as total_price
    FROM assignment_sql.products_q8 p
    INNER JOIN assignment_sql.order_items_q8 o
    ON o.product_id = p.product_id
)

SELECT
	category_id, 
    category_name,
    SUM(total_price) as total_sales
FROM (
		SELECT
			pts.product_id,
			pts.product_name,
			pts.category_id,
			cat.category_name,
			pts.price,
			pts.order_id,
			pts.quantity,
			pts.total_price
		FROM product_total_sales_cte pts
		INNER JOIN assignment_sql.categories_q8 cat
		ON pts.category_id = cat.category_id
) temp
GROUP BY category_id, category_name;

-- ================================================================================
-- QUESTION 9:
-- ================================================================================

-- Problem Statement:
-- For each employee, show their salary and the company's average salary.

CREATE TABLE assignment_sql.emp_scalar (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.emp_scalar VALUES
(1, 'Alice', 'IT', 80000),
(2, 'Bob', 'IT', 75000),
(3, 'Charlie', 'HR', 60000),
(4, 'Diana', 'HR', 55000),
(5, 'Eve', 'Sales', 70000);

SELECT * FROM assignment_sql.emp_scalar;

WITH avg_salary_cte as (
	select 
		ROUND(AVG(salary), 2) as avg_salary
	from assignment_sql.emp_scalar
) 
SELECT
	e.*,
    a.avg_salary,
    CAST(e.salary - a.avg_salary as signed) as diff
from assignment_sql.emp_scalar e
CROSS JOIN avg_salary_cte a;

-- ================================================================================
-- QUESTION 10:
-- ================================================================================

-- Problem Statement:
-- Find all students who have not enrolled in any course.

CREATE TABLE assignment_sql.students_q10 (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100)
);

CREATE TABLE assignment_sql.enrollments_q10 (
    enrollment_id INT PRIMARY KEY,
    student_id INT,
    course_id INT
);

INSERT INTO assignment_sql.students_q10 VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie'),
(4, 'Diana'),
(5, 'Eve');

INSERT INTO assignment_sql.enrollments_q10 VALUES
(1, 1, 101),
(2, 1, 102),
(3, 2, 101),
(4, 4, 103);

select * from assignment_sql.students_q10;
select * from assignment_sql.enrollments_q10;

# option 1: Corelated query
select s.*
from assignment_sql.students_q10 s
Where NOT EXISTS (
	select
		1
	FROM assignment_sql.enrollments_q10 e
    where s.student_id = e.student_id
);

-- ================================================================================
-- QUESTION 11:
-- ================================================================================

-- Problem Statement:
-- Find all departments that have at least one employee earning more than 80000.

CREATE TABLE assignment_sql.departments_q11 (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50)
);

CREATE TABLE assignment_sql.employees_q11 (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    dept_id INT,
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.departments_q11 VALUES
(1, 'Engineering'),
(2, 'Sales'),
(3, 'HR'),
(4, 'Marketing');

INSERT INTO assignment_sql.employees_q11 VALUES
(1, 'Alice', 1, 90000),
(2, 'Bob', 1, 75000),
(3, 'Charlie', 2, 85000),
(4, 'Diana', 3, 60000),
(5, 'Eve', 3, 55000);

SELECT * FROM assignment_sql.departments_q11;
SELECT * FROM assignment_sql.employees_q11;

SELECT
	d.*
FROM assignment_sql.departments_q11 d
WHERE EXISTS (
	SELECT
		1
	FROM assignment_sql.employees_q11 e
    WHERE d.dept_id = e.dept_id and e.salary > 80000
);

-- ================================================================================
-- QUESTION 12:
-- ================================================================================

-- Problem Statement:
-- Generate all possible product-color combinations.

CREATE TABLE assignment_sql.products_q12 (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(50)
);

CREATE TABLE assignment_sql.colors_q12 (
    color_id INT PRIMARY KEY,
    color_name VARCHAR(20)
);

INSERT INTO assignment_sql.products_q12 VALUES
(1, 'T-Shirt'),
(2, 'Pants');

INSERT INTO assignment_sql.colors_q12 VALUES
(1, 'Red'),
(2, 'Blue'),
(3, 'Green');

SELECT * FROM assignment_sql.products_q12;
SELECT * FROM assignment_sql.colors_q12;

SELECT 
	p.product_name,
    c.color_name
FROM assignment_sql.products_q12 p
CROSS JOIN assignment_sql.colors_q12 c;

-- ================================================================================
-- QUESTION 13:
-- ================================================================================

-- Problem Statement:
-- Find employees who have never submitted an expense report.

CREATE TABLE assignment_sql.employees_q13 (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100)
);

CREATE TABLE assignment_sql.expenses_q13 (
    expense_id INT PRIMARY KEY,
    emp_id INT,
    amount DECIMAL(10,2),
    expense_date DATE
);

INSERT INTO assignment_sql.employees_q13 VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie'),
(4, 'Diana');

INSERT INTO assignment_sql.expenses_q13 VALUES
(1, 1, 500, '2024-01-10'),
(2, 1, 300, '2024-01-15'),
(3, 3, 450, '2024-01-20');

select * from assignment_sql.employees_q13;
select * from assignment_sql.expenses_q13;

SELECT 
	*
FROM assignment_sql.employees_q13 emp
WHERE NOT EXISTS (
	SELECT 
		1
	FROM assignment_sql.expenses_q13 exp
    WHERE emp.emp_id = exp.emp_id
);

-- ================================================================================
-- QUESTION 14:
-- ================================================================================

-- Problem Statement:
-- Find customers whose first order amount was above 500.

CREATE TABLE assignment_sql.orders_q14 (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.orders_q14 VALUES
(1, 101, '2024-01-05', 600),
(2, 101, '2024-01-15', 300),
(3, 102, '2024-01-10', 400),
(4, 102, '2024-01-20', 550),
(5, 103, '2024-01-08', 700),
(6, 104, '2024-01-12', 450);

WITH first_order_cte as (
	SELECT
		customer_id,
		min(order_date) as first_order_date
	FROM assignment_sql.orders_q14
	GROUP BY customer_id
)

SELECT
	o.*
FROM assignment_sql.orders_q14 o
INNER JOIN first_order_cte fo
on o.customer_id = fo.customer_id and o.order_date = fo.first_order_date and o.amount > 500;

-- ================================================================================
-- QUESTION 15:
-- ================================================================================

-- Problem Statement:
-- Find products that have been ordered more times than the average order count 
-- across all products.

CREATE TABLE assignment_sql.order_items_q15 (
    order_id INT,
    product_id INT,
    quantity INT
);

INSERT INTO assignment_sql.order_items_q15 VALUES
(1, 1, 2),
(2, 1, 3),
(3, 1, 1),
(4, 2, 2),
(5, 2, 1),
(6, 3, 4),
(7, 4, 1);

SELECT * FROM assignment_sql.order_items_q15;

WITH avg_order_count_cte as (
	SELECT  
		COUNT(*) / COUNT(distinct product_id) as avg_order_count
    FROM assignment_sql.order_items_q15
)

SELECT
	oi.product_id,
    COUNT(*) as total_product_order
FROM assignment_sql.order_items_q15 oi
CROSS JOIN avg_order_count_cte ao
GROUP BY oi.product_id, ao.avg_order_count
HAVING total_product_order > ao.avg_order_count;

-- ================================================================================
-- QUESTION 16:
-- ================================================================================

-- Problem Statement:
-- Combine customer lists from two regions, showing duplicates handling.

CREATE TABLE assignment_sql.customers_east (
    customer_id INT,
    customer_name VARCHAR(100)
);

CREATE TABLE assignment_sql.customers_west (
    customer_id INT,
    customer_name VARCHAR(100)
);

INSERT INTO assignment_sql.customers_east VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie');

INSERT INTO assignment_sql.customers_west VALUES
(3, 'Charlie'),
(4, 'Diana'),
(5, 'Eve');

select * from assignment_sql.customers_east
UNION
select * from assignment_sql.customers_west;

-- ================================================================================
-- QUESTION 17:
-- ================================================================================

-- Problem Statement:
-- Find products that are sold in both online and retail stores.


CREATE TABLE assignment_sql.online_products (
    product_id INT,
    product_name VARCHAR(100)
);

CREATE TABLE assignment_sql.retail_products (
    product_id INT,
    product_name VARCHAR(100)
);

INSERT INTO assignment_sql.online_products VALUES
(1, 'Laptop'),
(2, 'Mouse'),
(3, 'Keyboard'),
(4, 'Monitor');

INSERT INTO assignment_sql.retail_products VALUES
(2, 'Mouse'),
(3, 'Keyboard'),
(5, 'Printer'),
(6, 'Scanner');

-- select * from assignment_sql.online_products
-- INTERSECT
-- select * from assignment_sql.retail_products;

-- OR
select 
	*
FROM assignment_sql.online_products op
WHERE op.product_id IN (
	SELECT 
		rp.product_id
	FROM assignment_sql.retail_products rp
);

-- ================================================================================
-- QUESTION 18:
-- ================================================================================

-- Problem Statement:
-- Find employees who are in the payroll system but not in the HR system.

CREATE TABLE assignment_sql.hr_employees (
    emp_id INT,
    emp_name VARCHAR(100)
);

CREATE TABLE assignment_sql.payroll_employees (
    emp_id INT,
    emp_name VARCHAR(100)
);

INSERT INTO assignment_sql.hr_employees VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie');

INSERT INTO assignment_sql.payroll_employees VALUES
(1, 'Alice'),
(2, 'Bob'),
(4, 'Diana'),
(5, 'Eve');


SELECT * FROM assignment_sql.payroll_employees pe
WHERE pe.emp_id NOT IN (
	SELECT 
		he.emp_id
	FROM assignment_sql.hr_employees he
);


-- ================================================================================
-- QUESTION 19:
-- ================================================================================

-- Problem Statement:
-- Find all pairs of employees who work in the same department.

CREATE TABLE assignment_sql.emp_pairs_q19 (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50)
);

INSERT INTO assignment_sql.emp_pairs_q19 VALUES
(1, 'Alice', 'IT'),
(2, 'Bob', 'IT'),
(3, 'Charlie', 'IT'),
(4, 'Diana', 'HR'),
(5, 'Eve', 'HR');

select * from assignment_sql.emp_pairs_q19;

SELECT
	ep1.emp_name as employee_1,
    ep2.emp_name as employee_2,
    ep1.department
FROM assignment_sql.emp_pairs_q19 ep1
INNER JOIN assignment_sql.emp_pairs_q19 ep2
ON ep1.emp_id < ep2.emp_id AND ep1.department = ep2.department;

-- ================================================================================
-- QUESTION 20:
-- ================================================================================

-- Problem Statement:
-- Find employees who earn more than the highest salary in the Sales department.

CREATE TABLE assignment_sql.emp_nested (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.emp_nested VALUES
(1, 'Alice', 'IT', 95000),
(2, 'Bob', 'IT', 85000),
(3, 'Charlie', 'Sales', 70000),
(4, 'Diana', 'Sales', 75000),
(5, 'Eve', 'HR', 80000);

select * from assignment_sql.emp_nested;

SELECT
	*
FROM assignment_sql.emp_nested en1
WHERE en1.salary > (
	SELECT MAX(en2.salary) as max_sales_dept_salary
	FROM assignment_sql.emp_nested en2
    WHERE en2.department = "Sales"
);

-- ================================================================================
-- QUESTION 21:
-- ================================================================================

-- Problem Statement:
-- For each department, show the count of employees and the count of employees 
-- earning above 60000.

CREATE TABLE assignment_sql.emp_counts (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.emp_counts VALUES
(1, 'Alice', 'IT', 80000),
(2, 'Bob', 'IT', 55000),
(3, 'Charlie', 'IT', 70000),
(4, 'Diana', 'HR', 45000),
(5, 'Eve', 'HR', 65000);

select * from assignment_sql.emp_counts;

WITH total_department_employees_cte as (
	SELECT department, COUNT(*) as total_employees
	FROM assignment_sql.emp_counts 
	GROUP BY department
), total_employees_salary_above_60k_cte as (
	SELECT department, COUNT(*) as total_employees
	FROM assignment_sql.emp_counts 
    WHERE salary > 60000
	GROUP BY department
)
SELECT
	te1.department,
    te1.total_employees as total_count,
    te2.total_employees as above_60k_count
FROM total_department_employees_cte te1
INNER JOIN total_employees_salary_above_60k_cte te2
ON te1.department = te2.department;

-- ================================================================================
-- QUESTION 22:
-- ================================================================================

-- Problem Statement:
-- Calculate the count of orders by status for each month.

CREATE TABLE assignment_sql.orders_status (
    order_id INT PRIMARY KEY,
    order_date DATE,
    status VARCHAR(20)
);

INSERT INTO assignment_sql.orders_status VALUES
(1, '2024-01-05', 'Completed'),
(2, '2024-01-10', 'Pending'),
(3, '2024-01-15', 'Completed'),
(4, '2024-01-20', 'Cancelled'),
(5, '2024-02-05', 'Completed'),
(6, '2024-02-10', 'Pending'),
(7, '2024-02-15', 'Pending');

select 
	date_format(order_date, "%Y-%m") as month, 
    SUM(CASE WHEN status = "Completed" THEN 1 ELSE 0 END) as Completed,
    SUM(CASE WHEN status = "Pending" THEN 1 ELSE 0 END) as Pending,
    SUM(CASE WHEN status = "Cancelled" THEN 1 ELSE 0 END) as Cancelled
from assignment_sql.orders_status
group by month;

-- ================================================================================
-- QUESTION 23:
-- ================================================================================

-- Problem Statement:
-- Join employees to their bonus based on performance rating.

CREATE TABLE assignment_sql.employees_bonus (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    performance_rating VARCHAR(20)
);

CREATE TABLE assignment_sql.bonus_rates (
    rating VARCHAR(20),
    bonus_percentage DECIMAL(5,2)
);

INSERT INTO assignment_sql.employees_bonus VALUES
(1, 'Alice', 'Excellent'),
(2, 'Bob', 'Good'),
(3, 'Charlie', 'Average'),
(4, 'Diana', 'Excellent');

INSERT INTO assignment_sql.bonus_rates VALUES
('Excellent', 20.00),
('Good', 10.00),
('Average', 5.00);

select
	eb.emp_name,
    eb.performance_rating,
    br.bonus_percentage
from assignment_sql.employees_bonus eb
INNER JOIN  assignment_sql.bonus_rates br
on eb.performance_rating = br.rating;

-- ================================================================================
-- QUESTION 24:
-- ================================================================================

-- Problem Statement:
-- Find the department with the highest total salary expense.

CREATE TABLE assignment_sql.dept_salary (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO assignment_sql.dept_salary VALUES
(1, 'Alice', 'IT', 80000),
(2, 'Bob', 'IT', 75000),
(3, 'Charlie', 'HR', 60000),
(4, 'Diana', 'HR', 55000),
(5, 'Eve', 'Sales', 90000);

select
	department,
    SUM(salary) as total_salary
from assignment_sql.dept_salary
GROUP BY department
ORDER BY total_salary DESC
LIMIT 1;

-- ================================================================================
-- QUESTION 25:
-- ================================================================================

-- Problem Statement:
-- Find products whose price is greater than the price of any product in the 
-- 'Accessories' category.

CREATE TABLE assignment_sql.products_any (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

INSERT INTO assignment_sql.products_any VALUES
(1, 'Laptop', 'Electronics', 1000),
(2, 'Mouse', 'Accessories', 25),
(3, 'Keyboard', 'Accessories', 50),
(4, 'Monitor', 'Electronics', 300),
(5, 'USB Cable', 'Accessories', 10),
(6, 'Headphones', 'Electronics', 75);

select *
from assignment_sql.products_any p
WHERE price > ANY (
	SELECT price
	FROM assignment_sql.products_any
    WHERE category = "Accessories"
);

-- ================================================================================
-- QUESTION 26:
-- ================================================================================

-- Problem Statement:
-- Calculate total sales amount for each salesperson, split by quarter.

CREATE TABLE assignment_sql.sales_filter (
    sale_id INT PRIMARY KEY,
    salesperson VARCHAR(50),
    sale_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.sales_filter VALUES
(1, 'John', '2024-01-15', 1000),
(2, 'John', '2024-02-20', 1500),
(3, 'John', '2024-04-10', 2000),
(4, 'Mary', '2024-01-25', 800),
(5, 'Mary', '2024-05-15', 1200),
(6, 'Mary', '2024-06-20', 900);

select * from assignment_sql.sales_filter;

select 
	salesperson,
    CAST(SUM(CASE WHEN month(sale_date) in ("01", "02", "03") THEN amount END) as signed) as Q1, 
    CAST(SUM(CASE WHEN month(sale_date) in ("04", "05", "06") THEN amount END) as signed) as Q2,
    CAST(SUM(CASE WHEN month(sale_date) in ("07", "08", "09") THEN amount END) as signed) as Q3,
    SUM(CASE WHEN month(sale_date) in ("10", "11", "12") THEN amount END) as Q4
from assignment_sql.sales_filter
group by salesperson;

-- ================================================================================
-- QUESTION 27:
-- ================================================================================

-- Problem Statement:
-- For each customer, find their top 2 orders by amount.

CREATE TABLE assignment_sql.customers_lat (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE assignment_sql.orders_lat (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.customers_lat VALUES
(1, 'Alice'),
(2, 'Bob');

INSERT INTO assignment_sql.orders_lat VALUES
(1, 1, '2024-01-10', 500),
(2, 1, '2024-01-15', 300),
(3, 1, '2024-01-20', 700),
(4, 2, '2024-01-12', 400),
(5, 2, '2024-01-18', 600);

select * from assignment_sql.customers_lat;
select * from assignment_sql.orders_lat;

with ranked_cte as (
	select
		order_id,
		customer_id,
        amount,
        DENSE_RANK() OVER(partition by customer_id order by amount DESC) as rnk
	FROM assignment_sql.orders_lat
)

select 
    c.customer_name,
    r.order_id,
    r.amount
from assignment_sql.customers_lat c
inner join ranked_cte r
on c.customer_id = r.customer_id
where r.rnk <= 2;

-- ================================================================================
-- QUESTION 28:
-- ================================================================================

-- Problem Statement:
-- Generate a series of dates from 2024-01-01 to 2024-01-07.

-- Expected Output:
-- +------------+
-- | date_value |
-- +------------+
-- | 2024-01-01 |
-- | 2024-01-02 |
-- | 2024-01-03 |
-- | 2024-01-04 |
-- | 2024-01-05 |
-- | 2024-01-06 |
-- | 2024-01-07 |
-- +------------+

WITH recursive date_series as(
	-- 1. Anchor query
    SELECT "2024-01-01" as date_value
    UNION
    -- 2. Recursive query
    SELECT date_add(date_value, interval 1 day)
    from date_series
    where date_value < "2024-01-07"
)

SELECT * FROM date_series;

-- ================================================================================
-- QUESTION 29: String Aggregation with GROUP BY
-- ================================================================================

-- Problem Statement:
-- For each department, list all employee names as a comma-separated string.

CREATE TABLE assignment_sql.emp_string_agg (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department VARCHAR(50)
);

INSERT INTO assignment_sql.emp_string_agg VALUES
(1, 'Alice', 'IT'),
(2, 'Bob', 'IT'),
(3, 'Charlie', 'HR'),
(4, 'Diana', 'IT'),
(5, 'Eve', 'HR');

select 
	department,
    group_concat(emp_name) as employee_names
from assignment_sql.emp_string_agg
group by department;

-- ================================================================================
-- QUESTION 30:
-- ================================================================================

-- Problem Statement:
-- Find customers who have ordered the same product more than once in different 
-- orders, and show the product details and order count.

CREATE TABLE assignment_sql.customers_q30 (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100)
);

CREATE TABLE assignment_sql.products_q30 (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100)
);

CREATE TABLE assignment_sql.orders_q30 (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE
);

CREATE TABLE assignment_sql.order_items_q30 (
    order_id INT,
    product_id INT,
    quantity INT
);

INSERT INTO assignment_sql.customers_q30 VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie');

INSERT INTO assignment_sql.products_q30 VALUES
(1, 'Laptop'),
(2, 'Mouse'),
(3, 'Keyboard');

INSERT INTO assignment_sql.orders_q30 VALUES
(1, 1, '2024-01-10'),
(2, 1, '2024-01-20'),
(3, 2, '2024-01-15'),
(4, 1, '2024-01-25'),
(5, 3, '2024-01-18');

INSERT INTO assignment_sql.order_items_q30 VALUES
(1, 1, 1),
(1, 2, 2),
(2, 1, 1),
(2, 3, 1),
(3, 2, 3),
(4, 1, 2),
(5, 3, 1);


select * from assignment_sql.customers_q30;
select * from assignment_sql.products_q30;
select * from assignment_sql.orders_q30;
select * from assignment_sql.order_items_q30;

select 
	c.customer_name, 
    p.product_name,
    count(*) as times_ordered 
from assignment_sql.customers_q30 c
inner join assignment_sql.orders_q30 o
inner join assignment_sql.order_items_q30 oi
inner join assignment_sql.products_q30 p
on c.customer_id = o.customer_id and o.order_id = oi.order_id and oi.product_id = p.product_id
group by c.customer_name, p.product_name
having times_ordered > 1;
