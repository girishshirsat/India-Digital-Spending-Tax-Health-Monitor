CREATE TABLE IF NOT EXISTS dim_state(
    state_id INT PRIMARY KEY,
    state_name TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS dim_date(
    date_id INT PRIMARY KEY,
    year SMALLINT NOT NULL CHECK (year BETWEEN 2018 AND 2024),
    quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),

    CONSTRAINT unique_year_quarter UNIQUE (year, quarter)
);


CREATE TABLE IF NOT EXISTS dim_txn_type(
    txn_type_id INT PRIMARY KEY,
    txn_type TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS dim_return_type(
    return_type_id INT PRIMARY KEY,
    return_type TEXT NOT NULL UNIQUE
);





CREATE TABLE IF NOT EXISTS fact_upi_state_quarter(
    state_id INT NOT NULL REFERENCES dim_state(state_id),
    date_id INT NOT NULL REFERENCES dim_date(date_id),
    total_count BIGINT,
    total_amount BIGINT,
    big_drop BOOLEAN,
    PRIMARY KEY (state_id, date_id)
);



CREATE TABLE IF NOT EXISTS fact_upi_state_quarter_type (
    state_id INT NOT NULL,
    date_id INT NOT NULL,
    txn_type_id INT NOT NULL,
    txn_count BIGINT,
    txn_amount BIGINT,

    PRIMARY KEY (state_id, date_id, txn_type_id),

    FOREIGN KEY (state_id) REFERENCES dim_state(state_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (txn_type_id) REFERENCES dim_txn_type(txn_type_id)
);

CREATE TABLE IF NOT EXISTS fact_gst_state_quarter (
    state_id INT NOT NULL,
    date_id INT NOT NULL,
    return_type_id INT NOT NULL,
    eligible BIGINT,
    on_time BIGINT,
    late BIGINT,
    total_filed BIGINT,
    filing_pct NUMERIC CHECK (filing_pct BETWEEN 0 AND 100),
    invalid_negative BOOLEAN,
    suspect_zero_eligible BOOLEAN,

    PRIMARY KEY (state_id, date_id, return_type_id),

    FOREIGN KEY (state_id) REFERENCES dim_state(state_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (return_type_id) REFERENCES dim_return_type(return_type_id)
);


CREATE TABLE IF NOT EXISTS fact_cpi_state_quarter (
    state_id INT NOT NULL,
    date_id INT NOT NULL,
    cpi_yoy NUMERIC,
    n_months INT,
    cpi_yoy_negative BOOLEAN,

    PRIMARY KEY (state_id, date_id),

    FOREIGN KEY (state_id) REFERENCES dim_state(state_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);