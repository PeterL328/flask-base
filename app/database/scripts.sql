CREATE TABLE pothole (
    location  point NOT NULL,
    severity  SMALLINT DEFAULT 0,
    time   timestamp DEFAULT current_timestamp
);

CREATE TABLE raw_data (
    location  point NOT NULL,
    time   timestamp NOT NULL,
    z float8 NOT NULL
);