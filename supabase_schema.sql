CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  order_code TEXT UNIQUE,
  email TEXT,
  customer_email TEXT,
  full_name TEXT,
  phone TEXT,
  country TEXT,
  state TEXT,
  address TEXT,
  btc_address TEXT,
  payment_proof_url TEXT,
  payment_status TEXT,
  order_status TEXT,
  total_amount NUMERIC,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  order_items JSONB
);
ALTER TABLE orders DISABLE ROW LEVEL SECURITY;