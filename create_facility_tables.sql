-- create_facility_tables.sql
-- Run with: psql -U postgres -d kenya_health_access -f create_facility_tables.sql

-- Drop tables if they exist (be careful!)
DROP TABLE IF EXISTS temp_facilities CASCADE;
DROP TABLE IF EXISTS facilities_facility CASCADE;
DROP TABLE IF EXISTS facilities_facilitytype CASCADE;
DROP TABLE IF EXISTS locations_county CASCADE;

-- Create counties table (47 Kenyan counties)
CREATE TABLE locations_county (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(3),
    capital VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Kenyan counties
INSERT INTO locations_county (name, code, capital) VALUES
('Nairobi', '047', 'Nairobi City'),
('Mombasa', '001', 'Mombasa'),
('Kisumu', '042', 'Kisumu'),
('Kiambu', '022', 'Kiambu'),
('Nakuru', '032', 'Nakuru'),
('Uasin Gishu', '027', 'Eldoret'),
('Kakamega', '037', 'Kakamega'),
('Meru', '012', 'Meru'),
('Kilifi', '003', 'Kilifi'),
('Machakos', '016', 'Machakos'),
('Garissa', '007', 'Garissa'),
('Kajiado', '034', 'Kajiado'),
('Kericho', '035', 'Kericho'),
('Bungoma', '039', 'Bungoma'),
('Busia', '040', 'Busia'),
('Siaya', '041', 'Siaya'),
('Homa Bay', '043', 'Homa Bay'),
('Migori', '044', 'Migori'),
('Kisii', '045', 'Kisii'),
('Nyamira', '046', 'Nyamira'),
('Trans Nzoia', '026', 'Kitale'),
('Elgeyo-Marakwet', '028', 'Iten'),
('Nandi', '029', 'Kapsabet'),
('Baringo', '030', 'Kabarnet'),
('Laikipia', '031', 'Rumuruti'),
('Narok', '033', 'Narok'),
('Turkana', '023', 'Lodwar'),
('West Pokot', '024', 'Kapenguria'),
('Samburu', '025', 'Maralal'),
('Marsabit', '010', 'Marsabit'),
('Isiolo', '011', 'Isiolo'),
('Tharaka-Nithi', '013', 'Chuka'),
('Embu', '014', 'Embu'),
('Kitui', '015', 'Kitui'),
('Makueni', '017', 'Wote'),
('Taita Taveta', '006', 'Voi'),
('Kwale', '002', 'Kwale'),
('Lamu', '005', 'Lamu'),
('Tana River', '004', 'Hola'),
('Wajir', '008', 'Wajir'),
('Mandera', '009', 'Mandera'),
('Murang''a', '021', 'Murang''a'),
('Kirinyaga', '020', 'Kerugoya'),
('Nyandarua', '018', 'Ol Kalou'),
('Nyeri', '019', 'Nyeri'),
('Vihiga', '038', 'Vihiga');

-- Create facility types table
CREATE TABLE facilities_facilitytype (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(20) DEFAULT '🏥',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert facility types
INSERT INTO facilities_facilitytype (name, icon) VALUES
('National Referral Hospital', '🏥'),
('County Hospital', '🏥'),
('Sub-County Hospital', '🏥'),
('Health Centre', '🏥'),
('Dispensary', '🏥'),
('Medical Clinic', '🏥'),
('Nursing Home', '🏥'),
('Pharmacy', '💊'),
('Medical Laboratory', '🔬'),
('Maternity Home', '👶');

-- Create main facility table
CREATE TABLE facilities_facility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mfl_code VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    
    -- Location fields (simplified for direct import)
    county_name VARCHAR(100),
    county_id INTEGER REFERENCES locations_county(id),
    constituency VARCHAR(100),
    ward VARCHAR(100),
    town VARCHAR(100),
    
    -- Coordinates
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    coordinate_source VARCHAR(50) DEFAULT 'import',
    
    -- Contact
    phone VARCHAR(50),
    email VARCHAR(254),
    
    -- Facility details
    facility_type_name VARCHAR(100),
    facility_type_id INTEGER REFERENCES facilities_facilitytype(id),
    owner VARCHAR(100),
    beds INTEGER DEFAULT 0,
    cots INTEGER DEFAULT 0,
    
    -- Status
    is_24_hours BOOLEAN DEFAULT FALSE,
    operational_status VARCHAR(50) DEFAULT 'operational',
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    data_source VARCHAR(100) DEFAULT 'mfl_2015_import',
    in_charge VARCHAR(100),
    in_charge_title VARCHAR(100),
    postal_address TEXT,
    postal_code VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    CONSTRAINT valid_coords CHECK (
        (latitude IS NULL) OR 
        (latitude BETWEEN -5 AND 5 AND longitude BETWEEN 33 AND 42)
    )
);

-- Create indexes
CREATE INDEX idx_facility_county ON facilities_facility(county_name);
CREATE INDEX idx_facility_type ON facilities_facility(facility_type_name);
CREATE INDEX idx_facility_coords ON facilities_facility(latitude, longitude);
CREATE INDEX idx_facility_mfl ON facilities_facility(mfl_code);