-- average price by outward-code (first 4 chars), last 5 years
SELECT
    LEFT(postcode, 4)  AS outward_code,
    ROUND(AVG(price))  AS avg_price
FROM   emily_capstone
GROUP  BY outward_code
ORDER  BY avg_price DESC;
