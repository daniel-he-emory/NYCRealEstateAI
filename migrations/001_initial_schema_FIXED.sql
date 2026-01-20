-- NYC Real Estate AI - Supabase Schema Migration (FIXED)
-- PostgreSQL doesn't allow generated columns to reference other generated columns
-- This version expands formulas inline

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: Neighborhoods
-- ============================================================================
CREATE TABLE neighborhoods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    neighborhood_name TEXT NOT NULL UNIQUE,
    borough TEXT CHECK (borough IN ('Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island')),
    median_price NUMERIC(12,2),
    median_price_per_sqft NUMERIC(10,2),
    median_rent NUMERIC(10,2),
    avg_days_on_market INTEGER,
    price_change_yoy NUMERIC(5,2),
    avg_subway_access INTEGER,
    walk_score INTEGER CHECK (walk_score BETWEEN 0 AND 100),
    transit_score INTEGER CHECK (transit_score BETWEEN 0 AND 100),
    neighborhood_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Computed column: rent_to_price_ratio
ALTER TABLE neighborhoods ADD COLUMN rent_to_price_ratio NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN median_price > 0 THEN ROUND((median_rent * 12) / median_price * 100, 2)
            ELSE 0
        END
    ) STORED;

-- Indexes for neighborhoods
CREATE INDEX idx_neighborhoods_borough ON neighborhoods(borough);
CREATE INDEX idx_neighborhoods_median_price ON neighborhoods(median_price);

-- ============================================================================
-- TABLE 2: Properties
-- ============================================================================
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT NOT NULL,
    neighborhood_id UUID REFERENCES neighborhoods(id),
    listing_url TEXT,
    current_price NUMERIC(12,2) NOT NULL,
    original_price NUMERIC(12,2),
    price_history JSONB,
    days_on_market INTEGER,
    bedrooms INTEGER,
    bathrooms NUMERIC(3,1),
    sqft INTEGER,
    monthly_hoa NUMERIC(10,2),
    estimated_monthly_rent NUMERIC(10,2),
    has_elevator BOOLEAN DEFAULT false,
    has_doorman BOOLEAN DEFAULT false,
    has_parking BOOLEAN DEFAULT false,
    has_gym BOOLEAN DEFAULT false,
    has_roof_deck BOOLEAN DEFAULT false,
    pet_friendly BOOLEAN DEFAULT false,
    exposure TEXT CHECK (exposure IN ('North', 'South', 'East', 'West', 'Corner', 'Multiple', 'Unknown')),
    floor_level TEXT CHECK (floor_level IN ('Low (1-5)', 'Mid (6-15)', 'High (16-30)', 'Penthouse (31+)', 'Unknown')),
    floor_number INTEGER,
    subway_distance INTEGER,
    nearest_subway_lines TEXT,
    year_built INTEGER,
    last_sale_date DATE,
    last_sale_price NUMERIC(12,2),
    acris_record_id TEXT,
    buyer_fit_score NUMERIC(5,2),
    property_description TEXT,
    property_tags TEXT[],
    data_source TEXT CHECK (data_source IN ('StreetEasy', 'Zillow', 'Realtor.com', 'Manual', 'API')),
    status TEXT CHECK (status IN ('Active', 'In Contract', 'Sold', 'Delisted', 'Price Change')) DEFAULT 'Active',
    estimated_annual_taxes NUMERIC(10,2),
    estimated_insurance NUMERIC(10,2),
    estimated_utilities NUMERIC(10,2),
    property_management_fee NUMERIC(10,2),
    down_payment NUMERIC(12,2),
    interest_rate NUMERIC(5,4),
    loan_term_years INTEGER DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simple computed columns (don't reference other generated columns)
ALTER TABLE properties ADD COLUMN price_cut_count INTEGER
    GENERATED ALWAYS AS (
        CASE
            WHEN price_history IS NOT NULL
            THEN jsonb_array_length(price_history) - 1
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN total_cut_percent NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN original_price > 0 AND current_price > 0
            THEN ROUND((original_price - current_price) / original_price * 100, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN price_per_sqft NUMERIC(10,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN sqft > 0 THEN ROUND(current_price / sqft, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN hoa_percent_of_price NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN current_price > 0 THEN ROUND((monthly_hoa * 12) / current_price * 100, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN annual_rent NUMERIC(12,2)
    GENERATED ALWAYS AS (estimated_monthly_rent * 12) STORED;

ALTER TABLE properties ADD COLUMN rent_to_price_ratio NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN current_price > 0 THEN ROUND((estimated_monthly_rent * 12) / current_price * 100, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN appreciation_since_last_sale NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN last_sale_price > 0 AND current_price > 0
            THEN ROUND((current_price - last_sale_price) / last_sale_price * 100, 2)
            ELSE 0
        END
    ) STORED;

-- FIXED: distress_flag now expands all formulas inline from base columns
ALTER TABLE properties ADD COLUMN distress_flag TEXT
    GENERATED ALWAYS AS (
        CASE
            WHEN (
                CASE
                    WHEN original_price > 0 AND current_price > 0
                    THEN ROUND((original_price - current_price) / original_price * 100, 2)
                    ELSE 0
                END >= 10
                AND
                CASE
                    WHEN price_history IS NOT NULL
                    THEN jsonb_array_length(price_history) - 1
                    ELSE 0
                END >= 2
                AND days_on_market >= 60
            ) THEN 'High'
            WHEN (
                CASE
                    WHEN original_price > 0 AND current_price > 0
                    THEN ROUND((original_price - current_price) / original_price * 100, 2)
                    ELSE 0
                END >= 5
                OR
                CASE
                    WHEN price_history IS NOT NULL
                    THEN jsonb_array_length(price_history) - 1
                    ELSE 0
                END >= 1
                OR days_on_market >= 45
            ) THEN 'Medium'
            ELSE 'Low'
        END
    ) STORED;

-- Investment metric computed columns
ALTER TABLE properties ADD COLUMN total_annual_expenses NUMERIC(12,2)
    GENERATED ALWAYS AS (
        COALESCE(monthly_hoa * 12, 0) +
        COALESCE(estimated_annual_taxes, 0) +
        COALESCE(estimated_insurance, 0) +
        COALESCE(estimated_utilities, 0) +
        COALESCE(property_management_fee, 0)
    ) STORED;

ALTER TABLE properties ADD COLUMN net_operating_income NUMERIC(12,2)
    GENERATED ALWAYS AS (
        COALESCE(estimated_monthly_rent * 12, 0) - (
            COALESCE(monthly_hoa * 12, 0) +
            COALESCE(estimated_annual_taxes, 0) +
            COALESCE(estimated_insurance, 0) +
            COALESCE(estimated_utilities, 0) +
            COALESCE(property_management_fee, 0)
        )
    ) STORED;

ALTER TABLE properties ADD COLUMN cap_rate NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN current_price > 0 THEN ROUND(
                (COALESCE(estimated_monthly_rent * 12, 0) - (
                    COALESCE(monthly_hoa * 12, 0) +
                    COALESCE(estimated_annual_taxes, 0) +
                    COALESCE(estimated_insurance, 0) +
                    COALESCE(estimated_utilities, 0) +
                    COALESCE(property_management_fee, 0)
                )) / current_price * 100, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN gross_rent_multiplier NUMERIC(5,1)
    GENERATED ALWAYS AS (
        CASE
            WHEN estimated_monthly_rent * 12 > 0 THEN ROUND(current_price / (estimated_monthly_rent * 12), 1)
            ELSE 0
        END
    ) STORED;

ALTER TABLE properties ADD COLUMN loan_amount NUMERIC(12,2)
    GENERATED ALWAYS AS (current_price - COALESCE(down_payment, 0)) STORED;

-- Indexes for properties
CREATE INDEX idx_properties_neighborhood ON properties(neighborhood_id);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_price ON properties(current_price);
CREATE INDEX idx_properties_bedrooms ON properties(bedrooms);
CREATE INDEX idx_properties_distress_flag ON properties(distress_flag);
CREATE INDEX idx_properties_buyer_fit_score ON properties(buyer_fit_score DESC NULLS LAST);
CREATE INDEX idx_properties_created_at ON properties(created_at DESC);

-- ============================================================================
-- TABLE 3: ComparableSales
-- ============================================================================
CREATE TABLE comparable_sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bbl TEXT NOT NULL,
    address TEXT NOT NULL,
    building_name TEXT,
    unit_number TEXT,
    bedrooms INTEGER,
    bathrooms NUMERIC(3,1),
    sqft INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    sale_price NUMERIC(12,2) NOT NULL,
    prior_year_sale_price NUMERIC(12,2),
    neighborhood_id UUID REFERENCES neighborhoods(id),
    property_link UUID REFERENCES properties(id),
    comp_quality TEXT CHECK (comp_quality IN ('Excellent', 'Good', 'Fair', 'Poor')),
    data_source TEXT DEFAULT 'DOF',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Computed columns for ComparableSales
ALTER TABLE comparable_sales ADD COLUMN ppsf NUMERIC(10,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN sqft > 0 THEN ROUND(sale_price / sqft, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE comparable_sales ADD COLUMN prior_year_ppsf NUMERIC(10,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN sqft > 0 AND prior_year_sale_price > 0 THEN ROUND(prior_year_sale_price / sqft, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE comparable_sales ADD COLUMN yoy_ppsf_change NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN sqft > 0 AND prior_year_sale_price > 0 THEN
                ROUND((ROUND(sale_price / sqft, 2) - ROUND(prior_year_sale_price / sqft, 2)) / ROUND(prior_year_sale_price / sqft, 2) * 100, 2)
            ELSE 0
        END
    ) STORED;

ALTER TABLE comparable_sales ADD COLUMN yoy_price_change NUMERIC(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN prior_year_sale_price > 0 THEN ROUND((sale_price - prior_year_sale_price) / prior_year_sale_price * 100, 2)
            ELSE 0
        END
    ) STORED;

-- Indexes for comparable_sales
CREATE INDEX idx_comps_bbl ON comparable_sales(bbl);
CREATE INDEX idx_comps_sale_date ON comparable_sales(sale_date DESC);
CREATE INDEX idx_comps_property_link ON comparable_sales(property_link);
CREATE INDEX idx_comps_neighborhood ON comparable_sales(neighborhood_id);

-- ============================================================================
-- TABLE 4: HistoricalSales
-- ============================================================================
CREATE TABLE historical_sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id TEXT UNIQUE NOT NULL,
    recorded_date DATE,
    address TEXT,
    borough TEXT CHECK (borough IN ('Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island')),
    neighborhood_id UUID REFERENCES neighborhoods(id),
    sale_price NUMERIC(12,2),
    property_type TEXT CHECK (property_type IN ('Condo', 'Co-op', 'Townhouse', 'Multi-family', 'Other')),
    bedrooms INTEGER,
    sqft INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Computed column
ALTER TABLE historical_sales ADD COLUMN price_per_sqft NUMERIC(10,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN sqft > 0 THEN ROUND(sale_price / sqft, 2)
            ELSE 0
        END
    ) STORED;

-- Indexes
CREATE UNIQUE INDEX idx_historical_sales_document_id ON historical_sales(document_id);
CREATE INDEX idx_historical_sales_date ON historical_sales(recorded_date DESC);
CREATE INDEX idx_historical_sales_neighborhood ON historical_sales(neighborhood_id);

-- ============================================================================
-- TABLE 5: MarketMetrics
-- ============================================================================
CREATE TABLE market_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    neighborhood_id UUID REFERENCES neighborhoods(id),
    avg_price_per_sqft NUMERIC(10,2),
    median_sale_price NUMERIC(12,2),
    sales_volume INTEGER,
    avg_days_on_market INTEGER,
    inventory_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_market_metrics_date ON market_metrics(date DESC);
CREATE INDEX idx_market_metrics_neighborhood ON market_metrics(neighborhood_id);

-- ============================================================================
-- TABLE 6: BuyerSearches
-- ============================================================================
CREATE TABLE buyer_searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_input TEXT,
    parsed_criteria JSONB,
    beds_min INTEGER,
    beds_max INTEGER,
    baths_min NUMERIC(3,1),
    price_min NUMERIC(12,2),
    price_max NUMERIC(12,2),
    required_amenities TEXT[],
    max_subway_distance INTEGER,
    max_hoa_monthly NUMERIC(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Many-to-many relationship tables
CREATE TABLE buyer_search_neighborhoods (
    search_id UUID REFERENCES buyer_searches(id) ON DELETE CASCADE,
    neighborhood_id UUID REFERENCES neighborhoods(id) ON DELETE CASCADE,
    PRIMARY KEY (search_id, neighborhood_id)
);

CREATE TABLE buyer_search_matched_properties (
    search_id UUID REFERENCES buyer_searches(id) ON DELETE CASCADE,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    match_score NUMERIC(5,2),
    PRIMARY KEY (search_id, property_id)
);

-- Indexes
CREATE INDEX idx_buyer_searches_created_at ON buyer_searches(created_at DESC);
CREATE INDEX idx_buyer_search_neighborhoods_search ON buyer_search_neighborhoods(search_id);
CREATE INDEX idx_buyer_search_properties_search ON buyer_search_matched_properties(search_id);

-- ============================================================================
-- UPDATE TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to tables with updated_at
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_neighborhoods_updated_at BEFORE UPDATE ON neighborhoods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Enable but allow all for now
-- ============================================================================
ALTER TABLE neighborhoods ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE comparable_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_searches ENABLE ROW LEVEL SECURITY;

-- Allow public read access (adjust for production)
CREATE POLICY "Allow public read neighborhoods" ON neighborhoods FOR SELECT USING (true);
CREATE POLICY "Allow public read properties" ON properties FOR SELECT USING (true);
CREATE POLICY "Allow public read comps" ON comparable_sales FOR SELECT USING (true);
CREATE POLICY "Allow public read historical" ON historical_sales FOR SELECT USING (true);
CREATE POLICY "Allow public read metrics" ON market_metrics FOR SELECT USING (true);
CREATE POLICY "Allow public read searches" ON buyer_searches FOR SELECT USING (true);

-- Allow public insert (for demo - restrict in production)
CREATE POLICY "Allow public insert properties" ON properties FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert comps" ON comparable_sales FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert searches" ON buyer_searches FOR INSERT WITH CHECK (true);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active listings with full details
CREATE OR REPLACE VIEW active_listings AS
SELECT
    p.*,
    n.neighborhood_name,
    n.borough,
    n.median_price as neighborhood_median_price,
    n.rent_to_price_ratio as neighborhood_rent_ratio
FROM properties p
LEFT JOIN neighborhoods n ON p.neighborhood_id = n.id
WHERE p.status = 'Active'
ORDER BY p.buyer_fit_score DESC NULLS LAST;

-- View: High distress properties
CREATE OR REPLACE VIEW high_distress_properties AS
SELECT
    p.*,
    n.neighborhood_name,
    n.borough
FROM properties p
LEFT JOIN neighborhoods n ON p.neighborhood_id = n.id
WHERE p.distress_flag = 'High' AND p.status = 'Active'
ORDER BY p.total_cut_percent DESC;

-- View: Best investment opportunities (high cap rate, low GRM)
CREATE OR REPLACE VIEW investment_opportunities AS
SELECT
    p.*,
    n.neighborhood_name,
    n.borough
FROM properties p
LEFT JOIN neighborhoods n ON p.neighborhood_id = n.id
WHERE
    p.status = 'Active'
    AND p.cap_rate >= 3.5
    AND p.gross_rent_multiplier > 0
    AND p.gross_rent_multiplier <= 15
ORDER BY p.cap_rate DESC;
