-- Creating the table
CREATE TABLE random_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    age INTEGER,
    registration_date TIMESTAMP,
    city VARCHAR(255),
    salary NUMERIC(10, 2)
);

-- Function for generating random data
CREATE OR REPLACE FUNCTION random_string(length INTEGER) RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT string_agg(chr(floor(random() * 26)::int + CASE WHEN random() < 0.5 THEN 65 ELSE 97 END), '')
        FROM generate_series(1, length)
    );
END;
$$ LANGUAGE plpgsql;

-- Inserting 1000 random rows
INSERT INTO random_data (name, age, registration_date, city, salary)
SELECT
    CASE WHEN i % 20 = 0 THEN NULL ELSE random_string(10) END,
    CASE WHEN i % 20 = 1 THEN NULL ELSE floor(random() * (80 - 18 + 1)) + 18 END,
    CASE WHEN i % 20 = 2 THEN NULL ELSE NOW() - (random() * (NOW() - '2020-01-01'::TIMESTAMP)) END,
    CASE WHEN i % 20 = 3 THEN NULL ELSE random_string(15) END,
    CASE WHEN i % 20 = 4 THEN NULL ELSE (random() * 100000 + 10000)::NUMERIC(10, 2) END
FROM generate_series(1, 1000) AS i;

-- Updating some rows to have empty {name} 
UPDATE random_data
SET name = ''
WHERE id % 19 = 0; 