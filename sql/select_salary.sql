WITH low AS (
    SELECT 'Низкая' AS category, COUNT(*) AS count 
    FROM employees_income 
    WHERE income < 20000
),
med AS (
    SELECT 'Средняя' AS category, COUNT(*) AS count 
    FROM employees_income 
    WHERE income >= 20000 AND income <= 50000
),
high AS (
    SELECT 'Высокая' AS category, COUNT(*) AS count 
    FROM employees_income 
    WHERE income > 50000
)
SELECT * FROM low 
UNION ALL 
SELECT * FROM med
UNION ALL 
SELECT * FROM high;


-- or use CASE
SELECT
    CASE
        WHEN income < 20000 THEN 'Низкая'
        WHEN income <= 50000 THEN 'Средняя'
        ELSE 'Высокая'
    END AS category,
    COUNT(*) AS count
FROM employees_income
GROUP BY category;

