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
