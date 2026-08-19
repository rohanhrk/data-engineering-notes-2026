-- ================================================================================
-- QUESTION 1: Customer Retention Analysis
-- ================================================================================

-- Calculate monthly customer retention rate. A customer is "retained" if they 
-- made a purchase in both the current and previous month.

CREATE TABLE assignment_sql.purchases_ret (
    purchase_id INT PRIMARY KEY,
    customer_id INT,
    purchase_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.purchases_ret VALUES
(1, 101, '2024-01-15', 100),
(2, 102, '2024-01-20', 200),
(3, 103, '2024-01-25', 150),
(4, 101, '2024-02-10', 120),
(5, 102, '2024-02-15', 180),
(6, 104, '2024-02-20', 90),
(7, 101, '2024-03-05', 200),
(8, 104, '2024-03-10', 150);

select * from assignment_sql.purchases_ret;

WITH total_customer_each_month_cte as (
	SELECT date_format(purchase_date, "%Y-%m") as month, count(distinct customer_id) as total_customers 
    FROM assignment_sql.purchases_ret
    GROUP BY month
), retained_customers_cte as (
	SELECT date_format(p1.purchase_date, "%Y-%m") as month, SUM(CASE WHEN (p1.purchase_id > p2.purchase_id) AND (month(p1.purchase_date) -  month(p2.purchase_date)) = 1 THEN 1 ELSE 0 END) as retained_customers 
    FROM assignment_sql.purchases_ret p1
    INNER JOIN assignment_sql.purchases_ret p2
    ON p1.customer_id = p2.customer_id
    group by month
    ORDER BY month
)

SELECT 
	t.month,
    t.total_customers,
    r.retained_customers,
    ROUND((r.retained_customers/t.total_customers) * 100.0, 2) as retention_rate
FROM total_customer_each_month_cte t
INNER JOIN retained_customers_cte r
ON t.month = r.month;

-- OR
WITH monthly_customers AS (
    SELECT DISTINCT
        DATE_FORMAT(purchase_date, '%Y-%m') AS month,
        customer_id
    FROM assignment_sql.purchases_ret
),
retention_calc AS (
    SELECT 
        curr.month,
        COUNT(DISTINCT curr.customer_id) AS total_customers,
        COUNT(DISTINCT prev.customer_id) AS retained_customers
    FROM monthly_customers curr
    LEFT JOIN monthly_customers prev 
        ON curr.customer_id = prev.customer_id
        AND prev.month = DATE_FORMAT(
            DATE_SUB(STR_TO_DATE(CONCAT(curr.month, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH),
            '%Y-%m'
        )
    GROUP BY curr.month
)
SELECT 
    month,
    total_customers,
    retained_customers,
    ROUND(retained_customers * 100.0 / NULLIF(total_customers, 0), 2) AS retention_rate
FROM retention_calc
ORDER BY month;

-- ================================================================================
-- QUESTION 2: Inventory Turnover Calculation
-- ================================================================================

-- Problem Statement:
-- Calculate inventory turnover ratio for each product (Cost of Goods Sold / 
-- Average Inventory Value).

CREATE TABLE assignment_sql.inventory (
    product_id INT,
    record_date DATE,
    quantity INT,
    unit_cost DECIMAL(10,2)
);

CREATE TABLE assignment_sql.sales_inv (
    sale_id INT PRIMARY KEY,
    product_id INT,
    sale_date DATE,
    quantity_sold INT,
    unit_cost DECIMAL(10,2)
);

INSERT INTO assignment_sql.inventory VALUES
(1, '2024-01-01', 100, 10.00),
(1, '2024-01-15', 80, 10.00),
(1, '2024-01-31', 120, 10.00),
(2, '2024-01-01', 50, 20.00),
(2, '2024-01-15', 40, 20.00),
(2, '2024-01-31', 60, 20.00);

INSERT INTO assignment_sql.sales_inv VALUES
(1, 1, '2024-01-10', 30, 10.00),
(2, 1, '2024-01-20', 25, 10.00),
(3, 2, '2024-01-12', 15, 20.00),
(4, 2, '2024-01-25', 10, 20.00);

SELECT * FROM assignment_sql.inventory;
SELECT * FROM assignment_sql.sales_inv;

WITH avg_inv_per_product_cte as (
	SELECT 
		product_id,
        ROUND(avg(quantity * unit_cost), 2) as avg_inv
	FROM assignment_sql.inventory
    GROUP BY product_id
), total_sold_per_product_cte as (
	SELECT
		product_id,
        SUM(quantity_sold * unit_cost) as total_sold
    FROM assignment_sql.sales_inv
    GROUP BY product_id
)

SELECT
	a.product_id,
    t.total_sold as cogs,
    a.avg_inv,
    ROUND((t.total_sold/a.avg_inv),2) as inv_tunrnover_ratio
FROM avg_inv_per_product_cte a
INNER JOIN total_sold_per_product_cte t
on a.product_id = t.product_id;

-- ================================================================================
-- QUESTION 3: Funnel Analysis
-- ================================================================================

-- Problem Statement:
-- Calculate conversion rates through a user funnel: Visit -> Signup -> Purchase.

CREATE TABLE assignment_sql.user_events (
    event_id INT PRIMARY KEY,
    user_id INT,
    event_type VARCHAR(20),
    event_date DATE
);

INSERT INTO assignment_sql.user_events VALUES
(1, 101, 'Visit', '2024-01-01'),
(2, 102, 'Visit', '2024-01-01'),
(3, 103, 'Visit', '2024-01-02'),
(4, 104, 'Visit', '2024-01-02'),
(5, 105, 'Visit', '2024-01-03'),
(6, 101, 'Signup', '2024-01-01'),
(7, 102, 'Signup', '2024-01-02'),
(8, 103, 'Signup', '2024-01-03'),
(9, 101, 'Purchase', '2024-01-02'),
(10, 102, 'Purchase', '2024-01-03');

SELECT * FROM assignment_sql.user_events;

WITH unique_users_cte as (
	SELECT COUNT(DISTINCT user_id) as total_users
    FROM assignment_sql.user_events
), user_count_by_events_cte as (
	SELECT event_type, COUNT(*) as user_count
    FROM assignment_sql.user_events
    GROUP BY event_type
)
SELECT 
	uc.*,
    uu.*,
    ROUND((uc.user_count/uu.total_users) * 100, 2) as conversion_rate
FROM user_count_by_events_cte uc
CROSS JOIN unique_users_cte uu;

-- ================================================================================
-- QUESTION 4: Session Analysis
-- ================================================================================

-- Problem Statement:
-- Group user page views into sessions. A new session starts if there's more 
-- than 30 minutes gap between consecutive page views.


CREATE TABLE assignment_sql.page_views_sess (
    view_id INT PRIMARY KEY,
    user_id INT,
    page_name VARCHAR(50),
    view_time TIMESTAMP
);

INSERT INTO assignment_sql.page_views_sess VALUES
(1, 101, 'Home', '2024-01-01 10:00:00'),
(2, 101, 'Products', '2024-01-01 10:05:00'),
(3, 101, 'Cart', '2024-01-01 10:20:00'),
(4, 101, 'Home', '2024-01-01 11:00:00'),
(5, 101, 'Products', '2024-01-01 11:10:00'),
(6, 102, 'Home', '2024-01-01 09:00:00'),
(7, 102, 'Products', '2024-01-01 09:15:00');

select * from assignment_sql.page_views_sess;

WITH prev_view_time_cte as (
	select 
		view_id,
		user_id,
		page_name,
		view_time as curr_view_time,
		LAG(view_time) OVER(PARTITION BY user_id ORDER BY view_time) as prev_view_time,
        TIMESTAMPDIFF(
				minute, 
                LAG(view_time) OVER(PARTITION BY user_id ORDER BY view_time), 
                view_time
		) as diff_minutes
	from assignment_sql.page_views_sess
), new_session_mark_cte as (
	SELECT 
		view_id,
		user_id,
		page_name,
		curr_view_time,
		prev_view_time,
		CASE 
			WHEN diff_minutes is NULL OR diff_minutes > 30 THEN 1
			ELSE 0
		END as is_new_session
	FROM prev_view_time_cte
), running_sum as (
	SELECT
		view_id,
        user_id,
        page_name,
        curr_view_time,
        coalesce(prev_view_time, curr_view_time) as prev_view_time,
        SUM(is_new_session) OVER(PARTITION BY user_id ORDER BY curr_view_time) as session_id
	FROM new_session_mark_cte
)
SELECT 
	user_id, 
    session_id,
    MIN(curr_view_time) as session_start,
    MAX(curr_view_time) as session_end,
    COUNT(*) as page_count
FROM running_sum
GROUP BY user_id, session_id;

-- ================================================================================
-- QUESTION 5: Market Basket Analysis - Frequently Bought Together
-- ================================================================================

-- Problem Statement:
-- Find pairs of products that are frequently bought together in the same order.

CREATE TABLE assignment_sql.order_items_mba (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100)
);

INSERT INTO assignment_sql.order_items_mba VALUES
(1, 1, 'Bread'),
(1, 2, 'Butter'),
(1, 3, 'Milk'),
(2, 1, 'Bread'),
(2, 2, 'Butter'),
(3, 1, 'Bread'),
(3, 3, 'Milk'),
(4, 2, 'Butter'),
(4, 3, 'Milk'),
(5, 1, 'Bread'),
(5, 2, 'Butter');


SELECT * FROM assignment_sql.order_items_mba;

SELECT 
    oi1.product_name as product_1,
    oi2.product_name as product_2,
    COUNT(*) as paired_times
FROM 
	assignment_sql.order_items_mba oi1
INNER JOIN 
	assignment_sql.order_items_mba oi2
ON 
	oi1.order_id = oi2.order_id 
    AND oi1.product_id < oi2.product_id
GROUP BY 
	oi1.product_name,
    oi2.product_name;
    
-- ================================================================================
-- QUESTION 6: Time Series Gap Filling
-- ================================================================================

-- Problem Statement:
-- Fill in missing dates with zero sales for a continuous date series.

CREATE TABLE assignment_sql.daily_sales_gap (
    sale_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO assignment_sql.daily_sales_gap VALUES
('2024-01-01', 1000),
('2024-01-02', 1500),
('2024-01-04', 800),
('2024-01-06', 2000),
('2024-01-07', 1200);

WITH recursive sale_window_cte as (
	SELECT 
		MIN(sale_date) as start_date,
		MAX(sale_date) as end_date
	FROM assignment_sql.daily_sales_gap
), sale_rec as (
	SELECT start_date
    FROM sale_window_cte
    UNION
    SELECT date_add(sr.start_date, interval 1 day) as sale_date
    FROM sale_rec sr
    CROSS JOIN sale_window_cte sw
    WHERE sr.start_date < sw.end_date
)
SELECT 
	s.start_date as sale_date,
    ROUND(coalesce(d.amount, 0), 0) as amount
FROM sale_rec s
LEFT JOIN assignment_sql.daily_sales_gap d
ON s.start_date = d.sale_date