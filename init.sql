DO 'BEGIN
    CREATE TYPE order_status AS ENUM (''pending'', ''completed'', ''cancelled'');
EXCEPTION WHEN duplicate_object THEN
   NULL;  -- ignore the error
END;';

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id INTEGER NOT NULL CHECK (customer_id > 0),
    amount DECIMAL NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL,
    status order_status NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);