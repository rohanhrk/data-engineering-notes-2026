-- -------------------------------------------------------------
-- Q1. 185. Department Top Three Salaries
-- url: https://leetcode.com/problems/department-top-three-salaries/description/
-- -------------------------------------------------------------
WITH dense_rnk as (
    SELECT 
        *,
        DENSE_RANK() OVER(PARTITION BY departmentId ORDER BY salary DESC) as rnk
    FROM Employee
), top_3_salary_by_dept as (
    SELECT
        *
    FROM dense_rnk
    WHERE rnk <= 3
)
SELECT 
    d.name as Department,
    t.name as Employee,
    t.salary as Salary
FROM top_3_salary_by_dept t
INNER JOIN Department d
ON t.departmentId = d.id;

-- -------------------------------------------------------------
-- Q2. 262. Trips and Users
-- url: https://leetcode.com/problems/trips-and-users/
-- -------------------------------------------------------------
WITH cancelled_cte as (
    SELECT 
        t.request_at as day,
        t.status != "completed" as cancelled
    FROM trips t
    INNER JOIN users c
    ON t.client_id = c.users_id AND c.banned ="No"
    INNER JOIN users d
    ON t.driver_id = d.users_id AND d.banned = "No"
    WHERE t.request_at BETWEEN "2013-10-01" and "2013-10-03"
)
SELECT 
    day,
    ROUND((SUM(cancelled) / COUNT(cancelled)), 2) as "Cancellation Rate"
FROM cancelled_cte
GROUP BY day;

-- -------------------------------------------------------------
-- Q3. 3482. Analyze Organization Hierarchy
-- url: https://leetcode.com/problems/analyze-organization-hierarchy/
-- -------------------------------------------------------------
WITH RECURSIVE
    -- Hierarchy_levels
cte AS (    
    SELECT              -- Anchor Member
        employee_id,
        employee_name,
        1 AS level
    FROM Employees
    WHERE manager_id IS NULL

        UNION ALL

    SELECT              -- Recursive Member
        e.employee_id,
        e.employee_name,
        c.level + 1 AS level
    FROM Employees e
    JOIN cte c
        ON e.manager_id = c.employee_id
),
    -- (manager, employee) pairs
cte1 AS (   
    SELECT              -- Anchor Member
        employee_id AS manager_id,
        employee_id,
        salary
    FROM Employees 

        UNION ALL

    SELECT              -- Recursive Member
        c1.manager_id,
        e.employee_id,
        e.salary
    FROM cte1 c1
    JOIN Employees e
        ON c1.employee_id = e.manager_id
),
    -- basic aggregation
cte2 AS (
    SELECT 
        c.manager_id AS employee_id,
        COUNT(*) - 1 AS team_size,
        SUM(c.salary) AS budget
    FROM cte1 c
    GROUP BY c.manager_id
)
SELECT
    c.employee_id,
    c.employee_name,
    c.level,
    c2.team_size,
    c2.budget
FROM cte2 c2
LEFT JOIN cte c
    ON c.employee_id = c2.employee_id
ORDER BY c.level, c2.budget DESC, c.employee_id;


-- -------------------------------------------------------------
-- Q4. 3554. Find Category Recommendation Pairs
-- url: https://leetcode.com/problems/find-category-recommendation-pairs/description/
-- -------------------------------------------------------------
WITH joined_cte as (
    select 
        p1.user_id,
        p2.product_id,
        p2.category
    from ProductPurchases P1
    INNER JOIN ProductInfo P2
    on P1.product_id = p2.product_id
), self_joined_cte as (
    SELECT 
        j1.category as category1,
        j2.category as category2,
        COUNT(DISTINCT j1.user_id) as customer_count
    FROM joined_cte j1
    INNER JOIN joined_cte j2
    ON j1.category < j2.category and j1.user_id = j2.user_id
    GROUP BY category1,category2
    HAVING customer_count >= 3
)
SELECT *
FROM self_joined_cte
ORDER BY customer_count DESC, category1, category2;