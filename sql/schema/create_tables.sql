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