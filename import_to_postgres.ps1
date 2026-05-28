# import_to_postgres.ps1
param(
    [string]$CSVPath = "facility_data/final_facilities.csv",
    [string]$DBName = "kenya_health_access",
    [string]$DBUser = "postgres",
    [string]$DBPassword = "IamHim@123",
    [string]$DBHost = "localhost",
    [string]$DBPort = "5432"
)

Write-Host "🚀 PostgreSQL Import Script for Kenya Health Facilities" -ForegroundColor Cyan
Write-Host "=" * 60

# Step 1: Check if CSV exists
if (-not (Test-Path $CSVPath)) {
    Write-Host "❌ CSV file not found: $CSVPath" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found CSV: $CSVPath" -ForegroundColor Green

# Step 2: Prepare CSV for PostgreSQL (Skipped: Already processed by prepare_csv_for_copy.py)
Write-Host "`n📝 Using pre-prepared CSV for PostgreSQL..." -ForegroundColor Yellow
$preparedCSV = "facility_data/facilities_for_postgres.csv"

# python -c @" ... "@ is skipped
# Step 3: Set PostgreSQL password for psql
$env:PGPASSWORD = $DBPassword

# Step 4: Create database tables
Write-Host "`n📦 Creating database tables..." -ForegroundColor Yellow
$createTablesSQL = @"
DROP TABLE IF EXISTS temp_facilities_import CASCADE;

CREATE TABLE IF NOT EXISTS locations_county (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    code VARCHAR(3),
    capital VARCHAR(100)
);

INSERT INTO locations_county (name, code, capital) VALUES
('Nairobi', '047', 'Nairobi'), ('Mombasa', '001', 'Mombasa'), ('Kisumu', '042', 'Kisumu'),
('Kiambu', '022', 'Kiambu'), ('Nakuru', '032', 'Nakuru'), ('Uasin Gishu', '027', 'Eldoret'),
('Kakamega', '037', 'Kakamega'), ('Meru', '012', 'Meru'), ('Kilifi', '003', 'Kilifi'),
('Machakos', '016', 'Machakos'), ('Garissa', '007', 'Garissa'), ('Kajiado', '034', 'Kajiado'),
('Kericho', '035', 'Kericho'), ('Bungoma', '039', 'Bungoma'), ('Busia', '040', 'Busia'),
('Siaya', '041', 'Siaya'), ('Homa Bay', '043', 'Homa Bay'), ('Migori', '044', 'Migori'),
('Kisii', '045', 'Kisii'), ('Nyamira', '046', 'Nyamira'), ('Trans Nzoia', '026', 'Kitale'),
('Elgeyo-Marakwet', '028', 'Iten'), ('Nandi', '029', 'Kapsabet'), ('Baringo', '030', 'Kabarnet'),
('Laikipia', '031', 'Rumuruti'), ('Narok', '033', 'Narok'), ('Turkana', '023', 'Lodwar'),
('West Pokot', '024', 'Kapenguria'), ('Samburu', '025', 'Maralal'), ('Marsabit', '010', 'Marsabit'),
('Isiolo', '011', 'Isiolo'), ('Tharaka-Nithi', '013', 'Chuka'), ('Embu', '014', 'Embu'),
('Kitui', '015', 'Kitui'), ('Makueni', '017', 'Wote'), ('Taita Taveta', '006', 'Voi'),
('Kwale', '002', 'Kwale'), ('Lamu', '005', 'Lamu'), ('Tana River', '004', 'Hola'),
('Wajir', '008', 'Wajir'), ('Mandera', '009', 'Mandera'), ('Murang''a', '021', 'Murang''a'),
('Kirinyaga', '020', 'Kerugoya'), ('Nyandarua', '018', 'Ol Kalou'), ('Nyeri', '019', 'Nyeri'),
('Vihiga', '038', 'Vihiga')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS facilities_facilitytype (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    icon VARCHAR(20) DEFAULT '🏥'
);

INSERT INTO facilities_facilitytype (name, icon) VALUES
('National Referral Hospital', '🏥'), ('County Hospital', '🏥'), ('Sub-County Hospital', '🏥'),
('Health Centre', '🏥'), ('Dispensary', '🏥'), ('Medical Clinic', '🏥'), ('Nursing Home', '🏥'),
('Pharmacy', '💊'), ('Medical Laboratory', '🔬'), ('Maternity Home', '👶')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS facilities_facility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mfl_code VARCHAR(50) UNIQUE,
    name VARCHAR(255),
    county_name VARCHAR(100),
    county_id INTEGER REFERENCES locations_county(id),
    constituency VARCHAR(100),
    ward VARCHAR(100),
    town VARCHAR(100),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    coordinate_source VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(254),
    facility_type_name VARCHAR(100),
    facility_type_id INTEGER REFERENCES facilities_facilitytype(id),
    owner VARCHAR(100),
    beds INTEGER DEFAULT 0,
    cots INTEGER DEFAULT 0,
    is_24_hours BOOLEAN DEFAULT FALSE,
    operational_status VARCHAR(50) DEFAULT 'operational',
    is_verified BOOLEAN DEFAULT FALSE,
    data_source VARCHAR(100),
    in_charge VARCHAR(100),
    in_charge_title VARCHAR(100),
    postal_address TEXT,
    postal_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facility_county ON facilities_facility(county_name);
CREATE INDEX IF NOT EXISTS idx_facility_type ON facilities_facility(facility_type_name);
CREATE INDEX IF NOT EXISTS idx_facility_mfl ON facilities_facility(mfl_code);
"@

# Execute table creation
$createTablesSQL | psql -h $DBHost -p $DBPort -U $DBUser -d $DBName -v ON_ERROR_STOP=1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create tables" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Tables created successfully" -ForegroundColor Green

# Step 5: Import data using COPY
Write-Host "`n📥 Importing data using COPY..." -ForegroundColor Yellow

# Create temp table
$tempTableSQL = @"
DROP TABLE IF EXISTS temp_facilities_import;
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
"@

$tempTableSQL | psql -h $DBHost -p $DBPort -U $DBUser -d $DBName -v ON_ERROR_STOP=1

# Use COPY command
$copyCommand = "\copy temp_facilities_import FROM '$preparedCSV' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8', NULL '\N')"
$copyCommand | psql -h $DBHost -p $DBPort -U $DBUser -d $DBName -v ON_ERROR_STOP=1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ COPY command failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ COPY completed successfully" -ForegroundColor Green

# Step 6: Transform and insert data
Write-Host "`n🔄 Transforming and inserting data..." -ForegroundColor Yellow

$transformSQL = @"
-- Insert into main table
INSERT INTO facilities_facility (
    mfl_code, name, county_name, constituency, ward, town,
    latitude, longitude, coordinate_source,
    phone, email, facility_type_name, owner,
    beds, cots, is_24_hours, operational_status,
    data_source, in_charge, in_charge_title,
    postal_address, postal_code
)
SELECT 
    facility_code,
    SUBSTRING(name, 1, 255),
    INITCAP(TRIM(county)),
    SUBSTRING(constituency, 1, 100),
    SUBSTRING(COALESCE(location, sub_location), 1, 100),
    SUBSTRING(COALESCE(town, nearest_town), 1, 100),
    NULLIF(TRIM(latitude), '')::DECIMAL,
    NULLIF(TRIM(longitude), '')::DECIMAL,
    COALESCE(NULLIF(TRIM(coordinate_source), ''), 'import'),
    NULLIF(TRIM(COALESCE(official_mobile, official_landline)), ''),
    NULLIF(TRIM(official_email), ''),
    INITCAP(TRIM(type)),
    NULLIF(TRIM(owner), ''),
    COALESCE(NULLIF(TRIM(beds), '')::INTEGER, 0),
    COALESCE(NULLIF(TRIM(cots), '')::INTEGER, 0),
    open_24_hours IN ('yes', 'true', 'y', '1', 't'),
    COALESCE(NULLIF(TRIM(operational_status), ''), 'operational'),
    'mfl_2015_import',
    NULLIF(TRIM(in_charge), ''),
    NULLIF(TRIM(job_title_of_in_charge), ''),
    NULLIF(TRIM(official_address), ''),
    NULLIF(TRIM(post_code), '')
FROM temp_facilities_import
WHERE name IS NOT NULL AND TRIM(name) != '';

-- Update county_id
UPDATE facilities_facility f
SET county_id = c.id
FROM locations_county c
WHERE f.county_name ILIKE c.name OR c.name ILIKE f.county_name;

-- Update facility_type_id
UPDATE facilities_facility f
SET facility_type_id = t.id
FROM facilities_facilitytype t
WHERE f.facility_type_name ILIKE t.name OR t.name ILIKE f.facility_type_name;

-- Update coordinates that are out of bounds
UPDATE facilities_facility
SET latitude = NULL, longitude = NULL, coordinate_source = 'invalid'
WHERE latitude IS NOT NULL AND (latitude < -5 OR latitude > 5 OR longitude < 33 OR longitude > 42);

-- Show import statistics
SELECT 
    COUNT(*) as total_facilities,
    COUNT(county_id) as with_county,
    COUNT(facility_type_id) as with_type,
    COUNT(latitude) as with_coords,
    COUNT(phone) as with_phone
FROM facilities_facility
WHERE data_source = 'mfl_2015_import';
"@

$transformSQL | psql -h $DBHost -p $DBPort -U $DBUser -d $DBName

# Step 7: Show final statistics
Write-Host "`n📊 FINAL IMPORT STATISTICS" -ForegroundColor Cyan
Write-Host "=" * 60

$statsSQL = @"
SELECT 
    'Total Facilities' as metric, COUNT(*)::TEXT as value FROM facilities_facility WHERE data_source = 'mfl_2015_import'
UNION ALL
SELECT 'With County', COUNT(*)::TEXT FROM facilities_facility WHERE county_id IS NOT NULL AND data_source = 'mfl_2015_import'
UNION ALL
SELECT 'With Facility Type', COUNT(*)::TEXT FROM facilities_facility WHERE facility_type_id IS NOT NULL AND data_source = 'mfl_2015_import'
UNION ALL
SELECT 'With Coordinates', COUNT(*)::TEXT FROM facilities_facility WHERE latitude IS NOT NULL AND data_source = 'mfl_2015_import'
UNION ALL
SELECT 'With Phone', COUNT(*)::TEXT FROM facilities_facility WHERE phone IS NOT NULL AND phone != '' AND data_source = 'mfl_2015_import'
UNION ALL
SELECT '24 Hour Facilities', COUNT(*)::TEXT FROM facilities_facility WHERE is_24_hours = true AND data_source = 'mfl_2015_import'
ORDER BY 1;
"@

$statsSQL | psql -h $DBHost -p $DBPort -U $DBUser -d $DBName -t -A -F " | "

Write-Host "`n✅ IMPORT COMPLETE!" -ForegroundColor Green
Write-Host "📁 Data imported to database: $DBName" -ForegroundColor Cyan