CREATE OR REPLACE VIEW v_avg_price_outcode AS
SELECT
  split_part(postcode,' ',1) AS outcode,
  ROUND(AVG(price))          AS avg_price,
  COUNT(*)                   AS n_sales
FROM emily_capstone
GROUP BY outcode;