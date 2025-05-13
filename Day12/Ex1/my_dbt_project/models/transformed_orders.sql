{{
  config(
    materialized='table'
  )
}}

WITH orders_filtered AS (
  -- Lọc đơn hàng, loại bỏ các đơn đã hủy
  SELECT * FROM {{ source('raw_data', 'orders') }}
  WHERE status != 'cancelled'
),

order_stats AS (
  -- Tính toán thống kê cho từng khách hàng
  SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_order_value,
    MIN(created_at) as first_order_date,
    MAX(created_at) as most_recent_order
  FROM orders_filtered
  GROUP BY customer_id
)

-- Kết hợp thông tin khách hàng với thống kê đơn hàng
SELECT
  c.customer_id,
  c.name,
  c.email,
  COALESCE(s.order_count, 0) as order_count,
  COALESCE(s.total_spent, 0) as total_spent,
  s.avg_order_value,
  s.first_order_date,
  s.most_recent_order
FROM {{ source('raw_data', 'customers') }} c
LEFT JOIN order_stats s ON c.customer_id = s.customer_id
