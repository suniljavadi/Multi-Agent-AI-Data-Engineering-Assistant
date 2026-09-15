CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    region TEXT,
    segment TEXT,
    revenue REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL,
    is_active INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    amount REAL,
    status TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    line_amount REAL
);

CREATE TABLE IF NOT EXISTS etl_jobs (
    job_id INTEGER PRIMARY KEY,
    job_name TEXT,
    owner TEXT,
    schedule TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS etl_executions (
    execution_id INTEGER PRIMARY KEY,
    job_name TEXT,
    execution_ts TEXT,
    status TEXT,
    duration_minutes REAL,
    rows_processed INTEGER,
    error_type TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS etl_logs (
    log_id INTEGER PRIMARY KEY,
    job_name TEXT,
    execution_ts TEXT,
    log_level TEXT,
    message TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY,
    job_name TEXT,
    timestamp TEXT,
    error_type TEXT,
    error_message TEXT,
    root_cause TEXT,
    resolution TEXT,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY,
    title TEXT,
    category TEXT,
    content TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    severity TEXT,
    status TEXT,
    approved INTEGER
);
