-- ========================================================
-- exists and not exists
-- ========================================================

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(100),
    plan_type VARCHAR(30),
    signup_date DATE
);

CREATE TABLE feature_usage (
    usage_id INT PRIMARY KEY,
    user_id INT,
    feature_name VARCHAR(100),
    usage_date DATE,
    usage_count INT
);

INSERT INTO users
(user_id, user_name, plan_type, signup_date)
VALUES
(1, 'Amit Sharma', 'Free', '2026-05-01'),
(2, 'Priya Mehta', 'Pro', '2026-05-03'),
(3, 'Rahul Verma', 'Pro', '2026-05-05'),
(4, 'Sneha Kapoor', 'Enterprise', '2026-05-07'),
(5, 'Karan Singh', 'Free', '2026-05-10'),
(6, 'Neha Gupta', 'Pro', '2026-05-12'),
(7, 'Rohit Jain', 'Enterprise', '2026-05-15'),
(8, 'Anjali Rao', 'Free', '2026-05-18');

INSERT INTO feature_usage
(usage_id, user_id, feature_name, usage_date, usage_count)
VALUES
(101, 1, 'Dashboard', '2026-06-01', 5),
(102, 1, 'Report Export', '2026-06-03', 2),
(103, 2, 'Dashboard', '2026-06-01', 8),
(104, 2, 'AI Insights', '2026-06-05', 4),
(105, 2, 'Report Export', '2026-06-07', 3),
(106, 3, 'Dashboard', '2026-06-02', 6),
(107, 4, 'Dashboard', '2026-06-01', 10),
(108, 4, 'AI Insights', '2026-06-04', 7),
(109, 4, 'API Access', '2026-06-06', 12),
(110, 6, 'Report Export', '2026-06-03', 2),
(111, 7, 'Dashboard', '2026-06-02', 9),
(112, 7, 'API Access', '2026-06-08', 15);

select * from users;
select * from feature_usage;

-- Find users who have used the AI Insights feature at least once.
select *
from users u
where exists (
	select 
		1
	from feature_usage fu
    where fu.user_id = u.user_id and fu.feature_name = 'ai insights'
);

-- Find users who have never used the AI Insights feature.
select *
from users u
where not exists (
	select 
		1
	from feature_usage fu
    where fu.user_id = u.user_id and fu.feature_name = 'ai insights'
);

-- Find Pro or Enterprise users who have used both: AI Insights and Report 
select
	*
from users u
where u.plan_type in ('pro', 'enterprise') and exists (
	select 
		1
	from feature_usage fu
    where u.user_id = fu.user_id and fu.feature_name in ('AI Insights','Report Export')
);


-- ========================================================
-- ANY and ALL operation
-- ========================================================

CREATE TABLE cluster_costs (
    cluster_id INT PRIMARY KEY,
    cluster_name VARCHAR(100),
    environment VARCHAR(30),
    cloud_provider VARCHAR(30),
    workload_type VARCHAR(50),
    daily_cost DECIMAL(10,2)
);

INSERT INTO cluster_costs
(cluster_id, cluster_name, environment, cloud_provider, workload_type, daily_cost)
VALUES
(1, 'prod-etl-small', 'Production', 'AWS', 'Batch ETL', 420),
(2, 'prod-etl-medium', 'Production', 'AWS', 'Batch ETL', 650),
(3, 'prod-streaming-main', 'Production', 'AWS', 'Streaming', 900),
(4, 'dev-etl-test', 'Development', 'AWS', 'Batch ETL', 300),
(5, 'dev-spark-heavy', 'Development', 'AWS', 'Batch ETL', 700),
(6, 'qa-pipeline-validation', 'QA', 'AWS', 'Batch ETL', 500),
(7, 'analytics-adhoc-1', 'Analytics', 'GCP', 'Adhoc Analytics', 750),
(8, 'analytics-adhoc-2', 'Analytics', 'GCP', 'Adhoc Analytics', 950),
(9, 'ml-feature-build', 'ML', 'Azure', 'Feature Engineering', 1100),
(10, 'sandbox-experiment', 'Development', 'AWS', 'Experimentation', 200);

select * from cluster_costs;

-- Find non-production clusters whose daily cost is greater than at least one production 
select *
from cluster_costs
where environment != 'production' and daily_cost > ANY (
	select daily_cost from cluster_costs
	where environment = 'production'
);

-- Find non-production clusters whose daily cost is greater than all production clusters
select *
from cluster_costs
where environment != 'production' and daily_cost > ALL (
	select daily_cost from cluster_costs
	where environment = 'production'
);


-- ========================================================
-- UNION and UNION ALL
-- ========================================================
CREATE TABLE website_leads (
    lead_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50)
);

CREATE TABLE app_leads (
    lead_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50)
);

INSERT INTO website_leads
(lead_id, customer_name, email, city)
VALUES
(1, 'Amit Sharma', 'amit@example.com', 'Delhi'),
(2, 'Priya Mehta', 'priya@example.com', 'Mumbai'),
(3, 'Rahul Verma', 'rahul@example.com', 'Bangalore'),
(4, 'Sneha Kapoor', 'sneha@example.com', 'Pune');

INSERT INTO app_leads
(lead_id, customer_name, email, city)
VALUES
(101, 'Priya Mehta', 'priya@example.com', 'Mumbai'),
(102, 'Karan Singh', 'karan@example.com', 'Delhi'),
(103, 'Rahul Verma', 'rahul@example.com', 'Bangalore'),
(104, 'Neha Gupta', 'neha@example.com', 'Hyderabad');

select * from website_leads;
select * from app_leads;

-- Get a unique list of all leads from website and app.
select customer_name, email, city
from website_leads
UNION
select customer_name, email, city
from app_leads;

-- Get all leads from website and app, including duplicates.
select customer_name, email, city
from website_leads
UNION ALL
select customer_name, email, city
from app_leads;

-- Uber SQL Question
CREATE TABLE matches (
    id INT PRIMARY KEY,
    team_1 VARCHAR(100),
    team_2 VARCHAR(100),
    winner VARCHAR(100)
);

INSERT INTO matches
(id, team_1, team_2, winner)
VALUES
(1, 'India', 'Australia', 'India'),
(2, 'England', 'Sri Lanka', 'Sri Lanka'),
(3, 'New Zealand', 'India', 'New Zealand'),
(4, 'India', 'Sri Lanka', 'India'),
(5, 'England', 'India', 'India'),
(6, 'South Africa', 'West Indies', 'South Africa'),
(7, 'Australia', 'England', 'Australia'),
(8, 'West Indies', 'India', 'India'),
(9, 'South Africa', 'New Zealand', 'South Africa'),
(10, 'Australia', 'Sri Lanka', 'Australia'),
(11, 'West Indies', 'England', 'West Indies'),
(12, 'New Zealand', 'Sri Lanka', 'New Zealand');

select * from matches;

-- Given a matches table with team_1, team_2, and winner, 
-- generate the full points table with columns like team, played, won, lost, points

select 
	team,
    count(*) as played,
    sum(case when result = 'won' then 1 else 0 end) as won,
    sum(case when result = 'lost' then 1 else 0 end) as lost,
    sum(case when result = 'won' then 2 else 0 end) as points
from
	(select 
		team_1 as team,
		CASE
			WHEN winner = team_1 THEN 'won'
			else 'lost'
		END as result
	from matches
	UNION ALL
	select 
		team_2 as team,
		CASE
			WHEN winner = team_2 THEN 'won'
			else 'lost'
		END as result
	from matches) overall_result
group by team;
