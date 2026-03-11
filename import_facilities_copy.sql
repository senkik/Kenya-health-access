-- import_facilities_copy.sql
-- Run with: psql -U postgres -d kenya_health_access -f import_facilities_copy.sql

-- Step 1: Create temporary table matching your CSV structure
DROP TABLE IF EXISTS temp_facilities_import CASCADE;

CREATE TEMP TABLE temp_facilities_import (
    facility_code VARCHAR(50),
    name TEXT,
    province TEXT,
    county TEXT,
    district TEXT,
    division TEXT,
    type TEXT,
    owner TEXT,
    location TEXT,
    sub_location TEXT,
    description_of_location TEXT,
    constituency TEXT,
    nearest_town TEXT,
    beds TEXT,
    cots TEXT,
    official_landline TEXT,
    official_mobile TEXT,
    official_email TEXT,
    official_address TEXT,
    official_alternate_no TEXT,
    town TEXT,
    post_code TEXT,
    in_charge TEXT,
    job_title_of_in_charge TEXT,
    open_24_hours TEXT,
    open_weekends TEXT,
    operational_status TEXT,
    latitude TEXT,
    longitude TEXT,
    coordinate_source TEXT
);

-- Step 2: Import CSV using COPY
-- IMPORTANT: Adjust the path to your CSV file
\copy temp_facilities_import FROM 'C:/Users/loren/OneDrive/Documents/Codes/projectfish/kenya-health-access/facility_data/facilities_for_postgres.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8', NULL '\N');

-- Step 3: Show import stats
SELECT COUNT(*) as total_imported FROM temp_facilities_import;

-- Step 4: Clean and transform data
-- Update county names
UPDATE temp_facilities_import 
SET county = TRIM(INITCAP(county));

-- Update facility types
UPDATE temp_facilities_import 
SET type = TRIM(INITCAP(type));

-- Clean phone numbers
UPDATE temp_facilities_import 
SET official_mobile = REGEXP_REPLACE(official_mobile, '[^0-9]', '', 'g');

UPDATE temp_facilities_import 
SET official_landline = REGEXP_REPLACE(official_landline, '[^0-9]', '', 'g');

-- Step 5: Insert into main facility table
INSERT INTO facilities_facility (
    mfl_code,
    name,
    county_name,
    constituency,
    ward,
    town,
    latitude,
    longitude,
    coordinate_source,
    phone,
    email,
    facility_type_name,
    owner,
    beds,
    cots,
    is_24_hours,
    operational_status,
    data_source,
    in_charge,
    in_charge_title,
    postal_address,
    postal_code,
    created_at
)
SELECT 
    facility_code,
    SUBSTRING(name, 1, 255),
    county,
    SUBSTRING(constituency, 1, 100),
    SUBSTRING(COALESCE(location, sub_location), 1, 100),
    SUBSTRING(COALESCE(town, nearest_town), 1, 100),
    CASE 
        WHEN latitude ~ '^[-+]?[0-9]*\.?[0-9]+$' THEN latitude::DECIMAL
        ELSE NULL
    END,
    CASE 
        WHEN longitude ~ '^[-+]?[0-9]*\.?[0-9]+$' THEN longitude::DECIMAL
        ELSE NULL
    END,
    COALESCE(coordinate_source, 'import'),
    COALESCE(official_mobile, official_landline),
    official_email,
    type,
    owner,
    CASE WHEN beds ~ '^[0-9]+$' THEN beds::INTEGER ELSE 0 END,
    CASE WHEN cots ~ '^[0-9]+$' THEN cots::INTEGER ELSE 0 END,
    CASE 
        WHEN LOWER(open_24_hours) IN ('yes', 'true', 'y', '1') THEN TRUE
        ELSE FALSE
    END,
    COALESCE(operational_status, 'operational'),
    'mfl_2015_import',
    in_charge,
    job_title_of_in_charge,
    official_address,
    post_code,
    CURRENT_TIMESTAMP
FROM temp_facilities_import
WHERE name IS NOT NULL AND TRIM(name) != '';

-- Step 6: Update county_id based on county_name
UPDATE facilities_facility f
SET county_id = c.id
FROM locations_county c
WHERE f.county_name ILIKE c.name OR c.name ILIKE f.county_name;

-- Step 7: Update facility_type_id
UPDATE facilities_facility f
SET facility_type_id = t.id
FROM facilities_facilitytype t
WHERE f.facility_type_name ILIKE t.name OR t.name ILIKE f.facility_type_name;

-- Step 8: Validate imported data
SELECT 
    COUNT(*) as total_facilities,
    COUNT(CASE WHEN county_id IS NOT NULL THEN 1 END) as with_county,
    COUNT(CASE WHEN facility_type_id IS NOT NULL THEN 1 END) as with_type,
    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as with_coords,
    COUNT(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 END) as with_phone
FROM facilities_facility
WHERE data_source = 'mfl_2015_import';