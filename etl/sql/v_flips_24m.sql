DROP VIEW IF EXISTS v_flips_24m;

CREATE VIEW v_flips_24m AS
WITH ordered AS (
  SELECT
    postcode,
    address,
    date      AS sale_date,
    price     AS sale_price,
    ROW_NUMBER() OVER (
      PARTITION BY postcode, address
      ORDER BY date
    ) AS rn
  FROM clean_house_prices
  WHERE address IS NOT NULL
),
paired AS (
  SELECT
    cur.postcode,
    cur.address,
    cur.sale_date,
    nxt.sale_date   AS next_date,
    cur.sale_price,
    nxt.sale_price  AS next_price,
    (nxt.sale_date - cur.sale_date)::INT                        AS days_between,
    (((nxt.sale_date - cur.sale_date)::numeric) / 30.44)::INT    AS months_between
  FROM ordered cur
  JOIN ordered nxt
    ON nxt.postcode = cur.postcode
   AND nxt.address  = cur.address
   AND nxt.rn       = cur.rn + 1
)
SELECT
  postcode,
  address,
  sale_date,
  next_date,
  sale_price,
  next_price,
  months_between,
  ROUND((next_price - sale_price) * 100.0 / sale_price, 0)::INT AS pct_gain
FROM paired
WHERE months_between > 2
  AND months_between <= 24
  AND (next_price - sale_price) * 100.0 / sale_price BETWEEN 20 AND 1000;