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

 

