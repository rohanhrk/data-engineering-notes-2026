-- -------------------------------------------------------------
-- Q1. 3808. Find Emotionally Consistent Users
-- url: https://leetcode.com/problems/find-emotionally-consistent-users/description/
-- -------------------------------------------------------------
-- For each user, count the total number of reactions they have given.
-- Only include users who have reacted to at least 5 different content items.
WITH users_content_reactions_summary as (
    SELECT 
        user_id, 
        count(*) as total_reaction, 
        count(distinct content_id) as unique_content_items
    FROM reactions
    GROUP BY user_id
    HAVING unique_content_items >= 5
), 
each_reaction_count as (
    SELECT 
        user_id, 
        reaction,
        COUNT(*) as reactions_count
    FROM reactions
    GROUP BY user_id, reaction
)
-- A user is considered emotionally consistent if at least 60% of their reactions are of the same type.
SELECT 
    u.user_id,
    e.reaction as dominant_reaction,
    ROUND(e.reactions_count / u.total_reaction, 2) as reaction_ratio
FROM users_content_reactions_summary u
INNER JOIN each_reaction_count e
ON u.user_id = e.user_id
WHERE e.reactions_count / u.total_reaction >= 0.6
ORDER BY reaction_ratio DESC, u.user_id

-- -------------------------------------------------------------
-- Q2. 3716. Find Churn Risk Customers
-- url: https://leetcode.com/problems/find-churn-risk-customers/description/
-- -------------------------------------------------------------
# Write your MySQL query statement below
-- 1. finding starting date, current date, max monthly amount for each event
-- ex. 
-- user_id   |   start_event   |   last_event   |   max_historical_amount
-- 1         |   2024-01-01    |   2024-03-20   |   29.99
-- 2         |   2024-01-05    |   2024-03-15   |   29.99
WITH last_event_cte as (
    SELECT
        user_id,
        max(event_id) as last_event,
        min(event_date) as start_event_date,
        max(event_date) as last_event_date,
        max(monthly_amount) as max_historical_amount
    FROM subscription_events
    GROUP BY user_id 
), 

-- 2. Finding active user
-- ex.
-- user_id  |   current_plan    |   current_monthly_amount
-- 501      |   basic           |   9.99
-- 502      |   basic           |   9.99         
active_user as (
    SELECT 
        s.user_id, 
        s.plan_name as current_plan,
        s.monthly_amount as current_monthly_amount
    FROM subscription_events s
    INNER JOIN last_event_cte l
    ON s.user_id = l.user_id and s.event_id = l.last_event and s.event_type != 'cancel'
),

-- 3. Finding the users who has downgrade their plan during the events
-- ex.
-- user_id  |   event_type
-- 501      |   downgrade
downgrade_subscibers_cte as (
    SELECT
        DISTINCT 
        user_id,
        event_type
    FROM subscription_events
    WHERE event_type = 'downgrade'
)

SELECT 
    l.user_id,
    a.current_plan,
    a.current_monthly_amount,
    l.max_historical_amount,
    abs(timestampdiff(day, start_event_date, last_event_date)) as days_as_subscriber
FROM last_event_cte l
INNER JOIN active_user a
ON l.user_id = a.user_id 
    and a.current_monthly_amount / l.max_historical_amount < 0.5 
    and abs(timestampdiff(day, start_event_date, last_event_date)) >= 60
INNER JOIN downgrade_subscibers_cte d
ON l.user_id = d.user_id
ORDER BY days_as_subscriber DESC, user_id

-- -------------------------------------------------------------
-- Q3. 3705. Find Golden Hour Customers
-- url: https://leetcode.com/problems/find-golden-hour-customers/description/
-- -------------------------------------------------------------
WITH orders_rated_summary as (
    SELECT
        customer_id,
        COUNT(*) as total_orders,
        ROUND(SUM(order_rating) / COUNT(order_rating), 2) as average_rating ,
        (COUNT(order_rating) / COUNT(*)) * 100 as pct_rated_orders 
    FROM restaurant_orders
    GROUP BY customer_id 
    HAVING average_rating >= 4.0 AND pct_rated_orders >= 50 AND total_orders >= 3
),
peak_hour_orders as (
    SELECT 
        customer_id,
        COUNT(*) as total_peak_hour_orders
    FROM restaurant_orders
    WHERE time(order_timestamp) BETWEEN '11:00:00' AND '14:00:00'
        OR time(order_timestamp) BETWEEN '18:00:00' AND '21:00:00'
    GROUP BY customer_id 
)

-- -------------------------------------------------------------
-- Q4. 3657. Find Loyal Customers
-- url: https://leetcode.com/problems/find-loyal-customers/description/
-- -------------------------------------------------------------
WITH cust_trxn_summary_cte as (
    SELECT 
        customer_id,
        min(transaction_date) as first_transaction_date,
        max(transaction_date) as latest_transaction_date,
        COUNT(*) as total_transaction
    FROM customer_transactions
    GROUP BY customer_id

    /*
        101     2024-01-05      2024-02-20      4
        102     2024-01-10      2024-02-15      5
        103     2024-01-01      2024-01-03      3
        104     2024-01-01      2024-03-15      6
    */

), total_refund_count_cte as (
    SELECT
        customer_id,
        COUNT(*) as total_refund
    FROM customer_transactions
    WHERE transaction_type = 'refund'
    GROUP BY customer_id

    /*
        102     2
        104     1
    */

)

SELECT
    c.customer_id
FROM cust_trxn_summary_cte as c
LEFT JOIN total_refund_count_cte as t
ON c.customer_id = t.customer_id 
WHERE (c.total_transaction - COALESCE(t.total_refund, 0)) >= 3
    AND DATEDIFF(c.latest_transaction_date, c.first_transaction_date) >= 30
    AND (COALESCE(t.total_refund, 0) / c.total_transaction)  < 0.2
ORDER BY c.customer_id;


/*
    tbl1
    101     2024-01-05      2024-02-20      4
    102     2024-01-10      2024-02-15      5
    103     2024-01-01      2024-01-03      3
    104     2024-01-01      2024-03-15      6
    =======
    tb2
    102     2
    104     1

    101     2024-01-05      2024-02-20      4   NULL    NULL
    102     2024-01-10      2024-02-15      5   102     2
    103     2024-01-01      2024-01-03      3   NULL    NULL
    104     2024-01-01      2024-03-15      6   
*/

-- optimization 1
-- We can minimize the 2nd cte query and write this into the first cte 

WITH cust_trxn_summary_cte as (
    SELECT 
        customer_id,
        min(transaction_date) as first_transaction_date,
        max(transaction_date) as latest_transaction_date,
        SUM(CASE WHEN transaction_type = 'purchase' THEN 1 ELSE 0 END) as total_purchase_txn,
        SUM(CASE WHEN transaction_type = 'refund' THEN 1 ELSE 0 END) as total_refund_txn
    FROM customer_transactions
    GROUP BY customer_id

    /*
        101     2024-01-05      2024-02-20      4       0
        102     2024-01-10      2024-02-15      3       2
        103     2024-01-01      2024-01-03      3       0
        104     2024-01-01      2024-03-15      5       1
    */

)
SELECT
    customer_id
FROM cust_trxn_summary_cte
WHERE total_purchase_txn >= 3
    AND DATEDIFF(latest_transaction_date, first_transaction_date) >= 30
    AND (total_refund_txn / (total_purchase_txn + total_refund_txn))  < 0.2
ORDER BY customer_id;

-- optimization 2
SELECT 
    customer_id
FROM customer_transactions
GROUP BY customer_id
HAVING 
    SUM(CASE WHEN transaction_type = 'purchase' THEN 1 ELSE 0 END) >= 3
    AND DATEDIFF(max(transaction_date) , min(transaction_date) ) >= 30
    AND (
            SUM(CASE WHEN transaction_type = 'refund' THEN 1 ELSE 0 END) / 
            (
                SUM(CASE WHEN transaction_type = 'purchase' THEN 1 ELSE 0 END) + 
                SUM(CASE WHEN transaction_type = 'refund' THEN 1 ELSE 0 END)
            )
        )  < 0.2
-- -------------------------------------------------------------
-- Q5. 3642. Find Books with Polarized Opinions
-- url: https://leetcode.com/problems/find-books-with-polarized-opinions/description/
-- -------------------------------------------------------------
-- A book has polarized opinions if it has at least one rating ≥ 4 and at least one rating ≤ 2 -> reading_sessions
-- Only consider books that have at least 5 reading sessions -> reading_sessions
-- Calculate the rating spread as (highest_rating - lowest_rating) -> reading_sessions
-- Calculate the polarization score as the number of extreme ratings (ratings ≤ 2 or ≥ 4) divided by total sessions -> reading_sessions
-- Only include books where polarization score ≥ 0.6 (at least 60% extreme ratings) -> reading_sessions

WITH reading_sessions_summary_cte as (
    SELECT
        book_id,
        SUM(CASE WHEN session_rating >= 4 THEN 1 ELSE 0 END) as is_rating_at_least_greater_than_4,
        SUM(CASE WHEN session_rating <= 2 THEN 1 ELSE 0 END) as is_rating_at_least_less_than_2,
        COUNT(*) as total_session,
        MAX(session_rating) - min(session_rating) as rating_spread,
        SUM(CASE 
                WHEN session_rating >= 4 or session_rating <= 2 THEN 1 
                ELSE 0 
            END) as extreme_ratings_count
    FROM reading_sessions 
    GROUP BY book_id 
)
SELECT
    b.book_id,
    b.title,
    b.author,
    b.genre,
    b.pages,
    r.rating_spread,
    ROUND(r.extreme_ratings_count / r.total_session, 2) as polarization_score
FROM books b
INNER JOIN reading_sessions_summary_cte r
ON b.book_id = r.book_id 
    AND r.is_rating_at_least_greater_than_4 >= 1 
    AND r.is_rating_at_least_less_than_2 >= 1
    AND r.total_session >= 5
    AND r.extreme_ratings_count / r.total_session >= 0.6
ORDER BY polarization_score DESC, b.title DESC;

-- OPTIMIZE
SELECT
    b.book_id,
    b.title,
    b.author,
    b.genre,
    b.pages,
    MAX(r.session_rating) - MIN(r.session_rating) as rating_spread,
    ROUND(
            SUM(CASE WHEN r.session_rating >= 4 or r.session_rating <= 2 THEN 1 ELSE 0 END) / COUNT(*), 
            2
        ) as polarization_score
FROM books b
INNER JOIN reading_sessions r
ON b.book_id = r.book_id 
GROUP BY b.book_id
HAVING 
    SUM(CASE WHEN r.session_rating >= 4 THEN 1 ELSE 0 END) >= 1 
    AND SUM(CASE WHEN r.session_rating <= 2 THEN 1 ELSE 0 END) >= 1
    AND COUNT(*) >= 5
    AND SUM(CASE WHEN r.session_rating >= 4 or r.session_rating <= 2 THEN 1 ELSE 0 END) / COUNT(*) >= 0.6
ORDER BY polarization_score DESC, b.title DESC;

-- -------------------------------------------------------------
-- Q6. 3626. Find Stores with Inventory Imbalance
-- url: https://leetcode.com/problems/find-stores-with-inventory-imbalance/description/
-- -------------------------------------------------------------
WITH inventory_summary_cte as (
    SELECT 
        store_id,
        MAX(price) as highest_price,
        MIN(price) as lowest_price,
        COUNT(DISTINCT product_name) as distinct_products
    FROM inventory 
    GROUP BY store_id 
    /*
        1   999.99  19.99   4
        2   699.99  15.99   4
        3   499.99  29.99   4
        4   299.99  49.99   2
        5   599.99  199.99  2
    */
), expensive_product_details as (
    SELECT
        i1.store_id,
        i1.highest_price,
        i1.distinct_products,
        i2.product_name,
        i2.quantity
    FROM inventory_summary_cte i1
    INNER JOIN inventory i2
    ON i1.store_id = i2.store_id
    AND i1.highest_price = i2.price
    AND i1.distinct_products >= 3

    /*
        1   999.99  4   Laptop  5
        2   699.99  4   Phone   3    
        3   499.99  4   
        4   299.99  2
        5   599.99  2
    */
), cheapest_product_details as (
    SELECT
        i1.store_id,
        i1.lowest_price,
        i1.distinct_products,
        i2.product_name,
        i2.quantity
    FROM inventory_summary_cte i1
    INNER JOIN inventory i2
    ON i1.store_id = i2.store_id
    AND i1.lowest_price = i2.price
    AND i1.distinct_products >= 3
)

SELECT
    s.store_id,
    s.store_name,
    s.location,
    e.product_name as most_exp_product,
    c.product_name as cheapest_product,
    ROUND(c.quantity/e.quantity, 2) as imbalance_ratio  
FROM expensive_product_details e
INNER JOIN cheapest_product_details c
ON e.store_id = c.store_id
AND e.quantity < c.quantity
INNER JOIN stores s
ON e.store_id = s.store_id
ORDER BY imbalance_ratio DESC, s.store_name

-- -------------------------------------------------------------
-- Q7. 3475. DNA Pattern Recognition 
-- url: https://leetcode.com/problems/dna-pattern-recognition/description/
-- -------------------------------------------------------------
SELECT
    *,
    CASE
        WHEN dna_sequence REGEXP "^ATG" THEN 1
        ELSE 0
    END as has_start,
    CASE
        WHEN dna_sequence LIKE "%TAA" or dna_sequence LIKE "%TAG" or dna_sequence LIKE "%TGA" THEN 1
        ELSE 0
    END as has_stop,
    CASE
        WHEN dna_sequence REGEXP ".?ATAT.?" THEN 1
        ELSE 0
    END as has_atat,
    CASE
        WHEN dna_sequence LIKE "%GGG%" THEN 1
        ELSE 0
    END as has_ggg
FROM Samples

-- -------------------------------------------------------------
-- Q8. 1393. Capital Gain/Loss
-- url: https://leetcode.com/problems/capital-gainloss/description/
-- -------------------------------------------------------------
WITH total_price_by_stock_each_op_cte as (
    SELECT
        stock_name,
        operation,
        SUM(price) as total_price
    FROM Stocks
    GROUP BY stock_name, operation
)
SELECT
    t1.stock_name,
    t2.total_price - t1.total_price as capital_gain_loss
FROM total_price_by_stock_each_op_cte t1
INNER JOIN total_price_by_stock_each_op_cte t2
ON t1.stock_name = t2.stock_name 
    AND t1.operation = 'Buy' 
    AND t2.operation = 'Sell'


-- -------------------------------------------------------------
-- Q9. 3497. Analyze Subscription Conversion 
-- url: https://leetcode.com/problems/analyze-subscription-conversion/description/
-- -------------------------------------------------------------
WITH avg_activity_durations_cte as (
    SELECT
        user_id,
        activity_type,
        ROUND(AVG(activity_duration), 2) as avg_activity_durations
    FROM UserActivity
    WHERE activity_type != 'cancelled'
    GROUP BY user_id, activity_type
)

SELECT 
    t1.user_id,
    t1.avg_activity_durations as trial_avg_duration,
    t2.avg_activity_durations as paid_avg_duration
FROM avg_activity_durations_cte t1
INNER JOIN avg_activity_durations_cte t2
ON t1.user_id = t2.user_id
AND t1.activity_type = 'free_trial' 
AND t2.activity_type = 'paid'
ORDER BY t1.user_id

-- -------------------------------------------------------------
-- Q10. 3220. Odd and Even Transactions
-- url: https://leetcode.com/problems/odd-and-even-transactions/
-- -------------------------------------------------------------
SELECT
    transaction_date,
    SUM(
        CASE
            WHEN amount % 2 != 0 THEN amount
            ELSE 0
        END
     ) as odd_sum,
    SUM(
        CASE
            WHEN amount % 2 = 0 THEN amount
            ELSE 0
        END
     ) as even_sum
FROM transactions
GROUP BY transaction_date
ORDER BY transaction_date;

-- -------------------------------------------------------------
-- Q11. 3564. Seasonal Sales Analysis
-- url: https://leetcode.com/problems/seasonal-sales-analysis/description/
-- -------------------------------------------------------------
WITH product_sale_by_seasons_cte as (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        s.quantity,
        s.price * s.quantity as revenue,
        CASE
            WHEN month(sale_date) in (12, 01, 02) THEN "Winter"
            WHEN month(sale_date) in (03, 04, 05) THEN "Spring"
            WHEN month(sale_date) in (06, 07, 08) THEN "Summer"
            ELSE "Fall"
        END as season
    FROM products p
    INNER JOIN sales s
    ON p.product_id = s.product_id
),
product_sale_grouped as (
    SELECT
        season,
        category,
        SUM(quantity) as total_quantity,
        SUM(revenue) as total_revenue
    FROM product_sale_by_seasons_cte
    GROUP BY season, category
),
ranking_cte as (
    SELECT
        *,
        ROW_NUMBER() OVER(
                            PARTITION BY season 
                            ORDER BY total_quantity DESC, 
                                     total_revenue DESC, 
                                     category
                         ) as rnk
    FROM product_sale_grouped
)
SELECT 
    season,
    category,
    total_quantity,
    total_revenue
FROM ranking_cte
WHERE rnk = 1


-- -------------------------------------------------------------
-- Q12. 3521. Find Product Recommendation Pairs
-- url: https://leetcode.com/problems/find-product-recommendation-pairs/description/
-- -------------------------------------------------------------
WITH product_details as (
    SELECT 
        p1.product_id,
        p1.category,
        p2.user_id
    FROM ProductInfo p1
    INNER JOIN ProductPurchases p2
    ON p1.product_id = p2.product_id
)

SELECT
    t1.product_id as product1_id, 
    t2.product_id as product2_id,
    t1.category as product1_category,
    t2.category as product2_category,
    COUNT(*) as customer_count
FROM product_details t1
INNER JOIN product_details t2
ON t1.user_id = t2.user_id and t1.product_id < t2.product_id
GROUP BY t1.product_id, t2.product_id, t1.category, t2.category
HAVING customer_count >= 3
ORDER BY customer_count DESC, product1_id, product2_id

-- -------------------------------------------------------------
-- Q13. 3601. Find Drivers with Improved Fuel Efficiency
-- url: https://leetcode.com/problems/find-drivers-with-improved-fuel-efficiency/description/
-- -------------------------------------------------------------
WITH both_halves_fuel_efficiency as (
    SELECT 
        driver_id,
        AVG(CASE WHEN month(trip_date) between 01 AND 06 THEN distance_km/fuel_consumed END) as first_half_avg,
        AVG(CASE WHEN month(trip_date) between 07 AND 12 THEN distance_km/fuel_consumed END) as second_half_avg
    FROM trips  
    GROUP BY driver_id
)
SELECT 
    d.driver_id,
    d.driver_name,
    ROUND(b.first_half_avg, 2) as first_half_avg,
    ROUND(b.second_half_avg, 2) as second_half_avg,
    ROUND(b.second_half_avg - b.first_half_avg, 2) as efficiency_improvement
FROM both_halves_fuel_efficiency b
INNER JOIN drivers d
ON b.driver_id = d.driver_id 
AND b.first_half_avg is not null 
AND b.second_half_avg - b.first_half_avg > 0
ORDER BY efficiency_improvement DESC, d.driver_name

-- -------------------------------------------------------------
-- Q14. 3421. Find Students Who Improved
-- url: https://leetcode.com/problems/find-students-who-improved/description/
-- -------------------------------------------------------------
WITH first_exam_score as (
    SELECT 
        *,
        ROW_NUMBER() OVER(PARTITION BY student_id, subject ORDER BY exam_date) as rnk
    FROM Scores 
), latest_exam_score as (
    SELECT 
        *,
        ROW_NUMBER() OVER(PARTITION BY student_id, subject ORDER BY exam_date DESC) as rnk
    FROM Scores 
)

SELECT
    f.student_id,
    f.subject,
    f.score as first_score,
    l.score as latest_score
FROM first_exam_score f
INNER JOIN latest_exam_score l
ON f.student_id = l.student_id
AND f.rnk = 1 
AND l.rnk = 1
AND f.subject = l.subject
AND f.exam_date != l.exam_date
AND l.score > f.score
ORDER BY f.student_id, f.subject

-- -------------------------------------------------------------
-- Q14. 3586. Find COVID Recovery Patients
-- url: https://leetcode.com/problems/find-covid-recovery-patients/
-- -------------------------------------------------------------
WITH first_positive_patients_cte as (
    SELECT
        patient_id,
        MIN(test_date) as first_positive_date
    FROM covid_tests
    WHERE result = 'Positive'
    GROUP BY patient_id
), first_negative_patients_cte as (
    SELECT
        c.patient_id,
        MIN(c.test_date) as first_negative_date
    FROM covid_tests c
    INNER JOIN first_positive_patients_cte f
    ON c.patient_id = f.patient_id 
    AND c.result = 'Negative' 
    AND f.first_positive_date < c.test_date
    GROUP BY f.patient_id
)
SELECT
    p.patient_id,
    p.patient_name,
    p.age,
    DATEDIFF(fn.first_negative_date, fp.first_positive_date) as recovery_time
FROM first_positive_patients_cte fp
INNER JOIN first_negative_patients_cte fn
ON fp.patient_id = fn.patient_id
AND fp.first_positive_date < fn.first_negative_date
INNER JOIN patients p
ON fp.patient_id = p.patient_id
ORDER BY recovery_time, patient_name