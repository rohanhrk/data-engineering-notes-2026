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