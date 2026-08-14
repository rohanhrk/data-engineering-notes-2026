-- ----------------------------------------------------------------------------
-- 1. REGISTER THE TWO RAW TOPICS
-- ----------------------------------------------------------------------------
CREATE STREAM checkout_events_row_stream (
    event_id VARCHAR,
    event_ts BIGINT,
    order_id VARCHAR,
    customer_id VARCHAR,
    customer_name VARCHAR,
    customer_email VARCHAR,
    customer_tier VARCHAR,
    product_id VARCHAR,
    product_name VARCHAR,
    category VARCHAR,
    quantity INTEGER,
    unit_price DOUBLE,
    discount_amount DOUBLE,
    currency VARCHAR,
    shipping_city VARCHAR,
    sales_channel VARCHAR
) WITH (
    KAFKA_TOPIC = 'ecommerce_checkout_events',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3,
    TIMESTAMP = 'event_ts'
);

CREATE STREAM payment_events_row_stream (
    event_id VARCHAR,
    event_ts BIGINT,
    order_id VARCHAR,
    payment_id VARCHAR,
    payment_method VARCHAR,
    payment_status VARCHAR,
    amount DOUBLE,
    currency VARCHAR,
    gateway VARCHAR,
    fraud_score DOUBLE,
    failure_reason VARCHAR
) WITH (
    KAFKA_TOPIC = 'ecommerce_payment_events',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3,
    TIMESTAMP = 'event_ts'
);

-- ----------------------------------------------------------------------------
-- 2. VALIDATE AND STANDARDIZE EACH INPUT STREAM
-- ----------------------------------------------------------------------------
-- A persistent query cleans the checkout records and derives the amount that
-- the payment service is expected to authorize.
CREATE STREAM valid_checkout_events_stream
WITH (
    KAFKA_TOPIC = 'ecommerce_valid_checkout_events',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS
SELECT 
    event_id,
    event_ts,
    order_id,
    customer_id,
    customer_name,
    customer_email,
    UCASE(customer_tier) AS customer_tier,
    product_id,
    product_name,
    UCASE(category) AS category,
    quantity,
    unit_price,
    discount_amount,
    ROUND((quantity * unit_price) - discount_amount, 2) AS expected_amount,
    UCASE(currency) AS currency,
    shipping_city,
    UCASE(sales_channel) AS sales_channel,
    CASE
        WHEN ((quantity * unit_price) - discount_amount) >= 20000 THEN 'HIGH'
        WHEN ((quantity * unit_price) - discount_amount) >= 5000 THEN 'MEDIUM'
        ELSE 'STANDARD'
    END AS order_value_band
FROM checkout_events_row_stream
WHERE order_id IS NOT NULL 
    AND customer_id IS NOT NULL
    AND quantity > 0
    AND unit_price > 0
    AND discount_amount >= 0
    AND discount_amount < (quantity * unit_price)
    AND currency IS NOT NULL
EMIT CHANGES;

-- Invalid records are retained in a separate topic instead of disappearing

CREATE STREAM rejected_checkout_events_stream 
WITH (
    KAFKA_TOPIC = 'ecommerce_rejected_checkout_events',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS
SELECT 
        *,
    CASE
        WHEN order_id IS NULL THEN 'MISSING_ORDER_ID'
        WHEN customer_id IS NULL THEN 'MISSING_CUSTOMER_ID'
        WHEN quantity IS NULL OR quantity <= 0 THEN 'INVALID_QUANTITY'
        WHEN unit_price IS NULL OR unit_price <= 0 THEN 'INVALID_UNIT_PRICE'
        WHEN discount_amount IS NULL OR discount_amount < 0 THEN 'INVALID_DISCOUNT'
        WHEN discount_amount >= (quantity * unit_price) THEN 'DISCOUNT_EXCEEDS_SUBTOTAL'
        WHEN currency IS NULL THEN 'MISSING_CURRENCY'
        ELSE 'UNKNOWN_VALIDATION_ERROR'
    END AS rejection_reason
FROM checkout_events_row_stream
WHERE order_id is NULL
    OR customer_id IS NULL
    OR quantity IS NULL 
    OR quantity <= 0
    OR unit_price IS NULL OR unit_price <= 0
    OR discount_amount IS NULL OR discount_amount < 0
    OR discount_amount >= (quantity * unit_price)
    OR currency is NULL
EMIT CHANGES;

CREATE STREAM valid_payment_events_stream
WITH (
    KAFKA_TOPIC = 'ecommerce_valid_payment_events',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS
SELECT
    event_id,
    event_ts,
    order_id,
    payment_id,
    UCASE(payment_method) AS payment_method,
    UCASE(payment_status) AS payment_status,
    amount,
    UCASE(currency) AS currency,
    UCASE(gateway) AS gateway,
    fraud_score,
    failure_reason
FROM payment_events_row_stream
WHERE order_id IS NOT NULL
    AND payment_id IS NOT NULL
    AND amount > 0 
    AND currency IS NOT NULL
    AND payment_status IS NOT NULL
    AND fraud_score BETWEEN 0.0 AND 1.0
EMIT CHANGES;


-- ----------------------------------------------------------------------------
-- 3. CORRELATE CHECKOUTS AND PAYMENTS IN EVENT TIME
-- ----------------------------------------------------------------------------
CREATE STREAM order_payment_decisions_stream
WITH (
    KAFKA_TOPIC = 'ecommerce_order_payment_decisions',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS
SELECT
    c.order_id AS order_id,
    c.event_id AS checkout_event_id,
    p.event_id AS payment_event_id,
    c.customer_id AS customer_id,
    c.customer_name AS customer_name,
    c.customer_email AS customer_email,
    c.customer_tier AS customer_tier,
    c.product_id AS product_id,
    c.product_name AS product_name,
    c.category AS category,
    c.quantity AS quantity,
    c.expected_amount AS expected_amount,
    p.amount AS paid_amount,
    c.currency AS order_currency,
    p.currency AS payment_currency,
    p.payment_id AS payment_id,
    p.payment_method AS payment_method,
    p.payment_status AS payment_status,
    p.gateway AS payment_gateway,
    p.fraud_score AS fraud_score,
    p.failure_reason AS failure_reason,
    c.shipping_city AS shipping_city,
    c.sales_channel AS sales_channel,
    c.order_value_band AS order_value_band,
    c.event_ts AS checkout_ts,
    p.event_ts AS payment_ts,
    (p.event_ts - c.event_ts) AS payment_latency_ms,
    TIMESTAMPTOSTRING(c.event_ts, 'yyyy-MM-dd HH:mm:ss', 'Asia/Kolkata')
        AS checkout_time_ist,
    TIMESTAMPTOSTRING(p.event_ts, 'yyyy-MM-dd HH:mm:ss', 'Asia/Kolkata')
        AS payment_time_ist,
    CASE
        WHEN p.payment_status <> 'AUTHORIZED' THEN 'PAYMENT_NOT_AUTHORIZED'
        WHEN c.currency <> p.currency THEN 'CURRENCY_MISMATCH'
        WHEN ABS(c.expected_amount - p.amount) > 1.0 THEN 'AMOUNT_MISMATCH'
        WHEN p.fraud_score >= 0.80 THEN 'HIGH_FRAUD_RISK'
        ELSE 'READY_FOR_FULFILLMENT'
    END AS decision,
    CASE
        WHEN p.payment_status = 'AUTHORIZED'
         AND c.currency = p.currency
         AND ABS(c.expected_amount - p.amount) <= 1.0
         AND p.fraud_score < 0.80
        THEN TRUE
        ELSE FALSE
    END AS is_fulfillment_ready
FROM valid_checkout_events_stream c
INNER JOIN valid_payment_events_stream p
    WITHIN 10 MINUTES
    GRACE PERIOD 2 MINUTES
ON c.order_id = p.order_id
EMIT CHANGES;


-- ----------------------------------------------------------------------------
-- 4. BRANCH THE JOIN RESULT INTO ACTIONABLE OUTPUT TOPICS
-- --------------------------------------------------------------------------
-- This is the main output consumed by the warehouse/fulfillment service.

CREATE STREAM fulfillment_ready_orders_stream
WITH (
    KAFKA_TOPIC = 'ecommerce_fullfillment_ready_orders',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS 
SELECT
    order_id,
    customer_id,
    customer_name,
    customer_email,
    product_id,
    product_name,
    quantity,
    paid_amount,
    payment_id,
    payment_method,
    shipping_city,
    order_value_band,
    checkout_time_ist,
    payment_time_ist,
    payment_latency_ms,
    'ALLOCATE_INVENTORY' AS next_action
FROM order_payment_decisions_stream
WHERE is_fulfillment_ready = TRUE
EMIT CHANGES;

-- Failed authorizations, mismatches, and high-risk orders go to manual review.
CREATE STREAM payment_review_orders_stream 
WITH (
    KAFKA_TOPIC = 'ecommerce_payment_review',
    KEY_FORMAT = 'KAFKA',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
)
AS
SELECT
    order_id,
    customer_id,
    customer_name,
    customer_email,
    payment_id,
    payment_status,
    expected_amount,
    paid_amount,
    fraud_score,
    failure_reason,
    decision,
    CASE
        WHEN decision = 'HIGH_FRAUD_RISK' THEN 'SEND_TO_FRAUD_TEAM'
        WHEN decision = 'AMOUNT_MISMATCH' THEN 'VERIFY_ORDER_TOTAL'
        WHEN decision = 'CURRENCY_MISMATCH' THEN 'VERIFY_CURRENCY'
        ELSE 'RETRY_OR_CONTACT_CUSTOMER'
    END AS next_action
FROM order_payment_decisions_stream
WHERE is_fulfillment_ready = FALSE
EMIT CHANGES;

-- ----------------------------------------------------------------------------
-- 5. BUILD A LIVE, WINDOWED OPERATIONS DASHBOARD
-- ----------------------------------------------------------------------------
CREATE TABLE payment_outcomes_5_minutes_table 
WITH (
    KAFKA_TOPIC = 'ecommerce_payment_outcomes_5_minutes',
    KEY_FORMAT = 'JSON',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 3
) AS
SELECT
    shipping_city,
    decision,
    COUNT(*) as order_count,
    ROUND(SUM(paid_amount), 2) as total_payment_amount,
    ROUND(AVG(fraud_score), 3) as average_fraud_score
FROM order_payment_decisions_stream
WINDOW TUMBLING (
    SIZE 5 MINUTES,
    GRACE PERIOD 2 MINUTES
)
GROUP BY shipping_city, decision
EMIT CHANGES;