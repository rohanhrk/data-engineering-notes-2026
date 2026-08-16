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
