-- TNC Accounts and Product Usage tracking for PME MCP products
-- Run on the shared thinkneo_mcp database

CREATE TABLE IF NOT EXISTS tnc_accounts (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(64) UNIQUE NOT NULL,
    key_prefix VARCHAR(8) NOT NULL,
    email VARCHAR(255),
    tnc_balance NUMERIC(12, 2) DEFAULT 1000.0,  -- Free trial: 1000 TNC
    tier VARCHAR(20) DEFAULT 'trial',            -- trial, starter, pro, enterprise
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ DEFAULT NOW(),
    stripe_customer_id VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS product_usage_log (
    id BIGSERIAL PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    product VARCHAR(50) NOT NULL,
    tnc_cost NUMERIC(8, 2) DEFAULT 1.0,
    ip VARCHAR(45),
    called_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_usage_key_month
    ON product_usage_log (key_hash, product, called_at);

CREATE INDEX IF NOT EXISTS idx_product_usage_product
    ON product_usage_log (product, called_at);

-- TNC top-up history
CREATE TABLE IF NOT EXISTS tnc_transactions (
    id BIGSERIAL PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    type VARCHAR(20) NOT NULL,  -- credit, debit, refund, bonus
    description TEXT,
    stripe_payment_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tnc_transactions_key
    ON tnc_transactions (key_hash, created_at);
