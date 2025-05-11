-- heatmap_outcode.sql
SELECT
  split_part(postcode,' ',1) AS outcode,
  AVG(price)                 AS avg_price,
  COUNT(*)                   AS n_sales
FROM clean_house_prices
GROUP BY outcode;
