CREATE TABLE classified_locations (
    id BIGINT PRIMARY KEY,
    original_address TEXT,
    fixed_variation TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    provider TEXT,
    classified_area TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
