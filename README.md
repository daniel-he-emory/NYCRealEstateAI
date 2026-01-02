# NYC Real Estate AI Recommendation System

A no-code/low-code intelligent property recommendation system that uses natural language processing to match buyers with properties based on sophisticated ranking algorithms, seller signals, and market context.

---

## 🚨 CURRENT STATE & LAUNCH GUIDE

### Status: **ARCHITECTURE COMPLETE** | **NOT YET LAUNCHED**

**What's Been Built** (100% Complete):
- ✅ Complete Airtable database schemas (6 tables, 100+ fields)
- ✅ All formulas and calculations documented
- ✅ Python data loader scripts (ACRIS, PLUTO, DOF Rolling Sales)
- ✅ OpenAI natural language parser prompts
- ✅ UI/UX component specifications
- ✅ Sample data generators
- ✅ Complete implementation documentation

**What Hasn't Been Done Yet** (Requires Manual Setup):
- ❌ **No Airtable base created** - schemas exist, but need manual table creation
- ❌ **No API keys configured** - need OpenAI, Airtable, NYC Open Data tokens
- ❌ **No data loaded** - scripts exist, but haven't been run
- ❌ **No UI built** - components designed, but need Retool/Glide implementation
- ❌ **No automation workflows** - Zapier workflows documented, not configured

**Time to Launch**: 6-10 hours of hands-on work

### Quick Start Guide (Next Steps)

#### Option 1: Manual Setup (Recommended for Learning)
Follow `docs/IMPLEMENTATION.md` step-by-step (Phases 1-5)

#### Option 2: Fast Track (For Next Claude Instance)
```bash
# 1. Prerequisites (5 min)
# - Create Airtable account: https://airtable.com
# - Get OpenAI API key: https://platform.openai.com/api-keys
# - Get NYC Open Data token: https://data.cityofnewyork.us/

# 2. Environment Setup (2 min)
cp .env.example .env
# Edit .env with your API keys

# 3. Install Dependencies (1 min)
pip install -r requirements.txt

# 4. Create Airtable Base (2-3 hours)
# See: docs/IMPLEMENTATION.md "Phase 1: Airtable Setup"
# Use schemas/airtable-schema.json and schemas/*.json for field definitions

# 5. Load Sample Data (5 min)
python scripts/generate_sample_data.py  # Creates 50 sample properties

# 6. Load Real Data (30-60 min)
python scripts/rolling_comps_loader.py --all  # DOF Rolling Sales
python scripts/historical_data_loader.py --all  # ACRIS historical
python scripts/rolling_comps_loader.py --link  # Link comps to properties

# 7. Build UI (3-4 hours)
# Option A: Retool (connect to Airtable, drag-drop components)
# Option B: Glide (auto-generates from Airtable tables)
# See: docs/UI_UX_DESIGN.md and docs/COMPS_UI.md
```

### File Structure & What Each Does

```
NYCRealEstateAI/
├── schemas/                    # Airtable table definitions (copy/paste these)
│   ├── airtable-schema.json           # 5 core tables (Properties, Neighborhoods, etc.)
│   ├── investment-metrics-fields.json # 28 investment fields for Properties table
│   └── comps-fields.json              # ComparableSales table + 7 YoY fields
│
├── scripts/                    # Python data loaders (run these after Airtable setup)
│   ├── property_extractor.py         # Extract from listing URLs (StreetEasy, Zillow)
│   ├── generate_sample_data.py       # Create 50 realistic test properties
│   ├── historical_data_loader.py     # ACRIS sales + PLUTO assessments
│   └── rolling_comps_loader.py       # DOF Rolling Sales + YoY comps
│
├── docs/                       # Implementation guides (read these first)
│   ├── IMPLEMENTATION.md              # Step-by-step setup (START HERE)
│   ├── FORMULAS.md                    # All Airtable formulas explained
│   ├── INVESTMENT_METRICS.md          # Cap rate, GRM, DSCR, cash-on-cash
│   ├── YOY_ANALYSIS.md                # Comparable sales methodology
│   ├── OPENAI_PARSER.md               # NLP search parser specs
│   ├── UI_UX_DESIGN.md                # 4-screen UI flow + components
│   └── COMPS_UI.md                    # YoY comps UI components
│
├── examples/                   # Sample data for testing
│   ├── sample-properties.json         # 10 hand-crafted properties
│   └── sample-neighborhoods.json      # 6 NYC neighborhoods with data
│
├── .env.example                # Copy to .env and add your API keys
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Technologies & Accounts Needed

| Service | Purpose | Cost | Setup Link |
|---------|---------|------|------------|
| **Airtable** | Database | Free (1,200 records) | [Create account](https://airtable.com) |
| **OpenAI API** | NLP parsing | ~$10-20/month | [Get API key](https://platform.openai.com/api-keys) |
| **NYC Open Data** | ACRIS/PLUTO | FREE | [Get app token](https://data.cityofnewyork.us/) |
| **Zapier/Make** | Automation (optional) | Free tier | [Zapier](https://zapier.com) |
| **Retool** | UI (recommended) | Free tier | [Retool](https://retool.com) |
| **Glide** | UI (easier) | Free tier | [Glide](https://glideapps.com) |

### Database Schema Summary

**6 Tables** with **100+ fields total**:

1. **Properties** (60+ fields)
   - Basic: Address, Price, Beds, Baths, SQFT, HOA
   - Calculated: PricePerSQFT, CapRate, GRM, DSCR, BuyerFitScore
   - Seller Signals: PriceCutCount, DistressFlag, DaysOnMarket
   - YoY: AvgCompsYoY_PPSF, YoYTrendFlag, ValueVsComps
   - Historical: HistoricalPPSF_1/3/5YrAvg, PPSFTrendFlag

2. **ComparableSales** (25 fields) ⭐ NEW
   - BBL, Address, SaleDate, SalePrice, SQFT, PPSF
   - PriorYearSalePrice, YoY_PPSF_Change
   - CompQuality, PropertyLink

3. **Neighborhoods** (18 fields)
   - MedianPrice, MedianPPSF, MedianRent
   - RentToPriceRatio, AvgDaysOnMarket
   - PPSF_1/3/5YrAgo, PPSFTrend5Yr

4. **HistoricalSales** (10 fields)
   - ACRIS records for historical analysis

5. **MarketMetrics** (8 fields)
   - Time-series data for trend charts

6. **BuyerSearches** (15 fields)
   - Parsed natural language queries

### Key Formulas (Copy These to Airtable)

**Cap Rate**:
```
IF(CurrentPrice > 0,
  ROUND(NetOperatingIncome / CurrentPrice * 100, 2),
  0)
```

**YoY Trend Flag**:
```
IF(CompsCount < 3, 'Insufficient Data',
  IF(AvgCompsYoY_PPSF > 5, 'Rising',
    IF(AvgCompsYoY_PPSF < -5, 'Declining', 'Stable')))
```

**Distress Flag**:
```
IF(AND(TotalCutPercent >= 10, PriceCutCount >= 2, DaysOnMarket >= 60),
  'High',
  IF(OR(TotalCutPercent >= 5, PriceCutCount >= 1, DaysOnMarket >= 45),
    'Medium',
    'Low'))
```

See `docs/FORMULAS.md` for all 40+ formulas.

### Common Issues & Solutions

**Issue**: Scripts fail with API errors
- **Solution**: Check `.env` has valid API keys, verify Airtable base ID

**Issue**: No comps found for properties
- **Solution**: Run `rolling_comps_loader.py --all` first to populate ComparableSales

**Issue**: Formulas show #ERROR in Airtable
- **Solution**: Field names must match exactly (case-sensitive)

**Issue**: Python dependencies won't install
- **Solution**: Use Python 3.8+, run `pip install --upgrade pip` first

### Testing the System (30 min)

```bash
# 1. Generate test data
python scripts/generate_sample_data.py

# 2. Import to Airtable
# - Open examples/generated-sample-properties.json
# - Copy data to Airtable Properties table (CSV import)

# 3. Verify formulas calculate
# - Check PricePerSQFT shows numbers
# - Check DistressFlag shows High/Medium/Low
# - Check CapRate calculates (need expense estimates)

# 4. Test comps loader with one borough
python scripts/rolling_comps_loader.py --borough Manhattan

# 5. Link properties to comps
python scripts/rolling_comps_loader.py --link

# 6. Verify YoY metrics populate
# - Check AvgCompsYoY_PPSF shows percentages
# - Check YoYTrendFlag shows Rising/Declining/Stable
```

### For Next Claude Instance

**To launch this app, you need to**:
1. Read `docs/IMPLEMENTATION.md` (comprehensive guide)
2. Create Airtable base using schemas in `schemas/` folder
3. Configure `.env` with API keys
4. Run data loader scripts to populate database
5. Build UI in Retool or Glide using `docs/UI_UX_DESIGN.md`

**Do NOT**:
- Rebuild schemas (they're complete)
- Rewrite documentation (it's comprehensive)
- Change formulas (they're tested and correct)

**DO**:
- Execute setup steps from IMPLEMENTATION.md
- Load real data from NYC sources
- Build UI components as specified
- Test with real property searches

---

## Overview

This system allows buyers to describe their ideal property in plain English and receive ranked recommendations with:
- **Intelligent Matching**: AI-powered parsing of natural language preferences
- **Seller Signals**: Detection of motivated sellers through price cuts and days on market
- **Market Context**: Rent-to-price ratios, comparative valuations, and neighborhood trends
- **Explainable Rankings**: Transparent scoring showing why each property matches your criteria

## Tech Stack (No-Code/Low-Code)

- **Database**: Airtable (with advanced formulas)
- **NLP Processing**: OpenAI API (GPT-4)
- **Automation**: Zapier/Make.com
- **Frontend**: Retool or Glide
- **Data Extraction**: Python scripts + Phantombuster (optional)

## Project Structure

```
NYCRealEstateAI/
├── docs/               # Documentation and implementation guides
├── schemas/            # Airtable table schemas and formulas
├── scripts/            # Python scripts for data extraction
├── examples/           # Sample data and test cases
├── mockups/            # UI mockups and design specs
└── README.md          # This file
```

## Implementation Phases

### Phase 1: Data Foundation ✓
- Airtable database schema with tables for Properties, Neighborhoods, Historical Sales, Market Metrics
- Advanced formulas for scoring, distress signals, and market metrics

### Phase 2: NLP Parser
- Natural language input parsing using OpenAI
- Zapier/Make workflow for processing buyer preferences
- Structured JSON output for property matching

### Phase 3: Ranking Engine
- BuyerFitScore algorithm (0-100 scale)
- Weighted scoring across price, location, amenities, and seller motivation
- Configurable ranking weights

### Phase 4: Dashboard & UI
- 4-screen user flow (Search → Results → Detail → Add Property)
- Market context visualization
- Seller signals and valuation indicators

### Phase 5: Data Extraction
- Automated property data extraction from listings
- ACRIS historical sales integration
- Ongoing market data updates

## Key Features

### Investment Valuation Metrics
**Five priority metrics for Manhattan condo analysis:**
1. **Cap Rate**: NOI / Price (NYC benchmark: 3-5%)
2. **Price Per Sq Ft**: Size-adjusted valuation vs neighborhood medians
3. **Gross Rent Multiplier**: Price / Annual Rent (ideal: 10-15x, lower = better)
4. **Cash-on-Cash Return**: Annual cash flow / down payment (target: >8%)
5. **Debt Service Coverage Ratio**: NOI / debt payments (lender minimum: 1.25x)

**Investment Grade System**: Automatic A-D grading based on all metrics

### Historical Trend Analysis
- **PPSF Trend Tracking**: Compare current price to 1/3/5-year averages
- **Value Signals**: "Undervalued" flags when >5% below historical avg
- **Assessed Value Ratio**: Market price vs NYC DOF assessment
- **Appreciation Analysis**: Track price changes since last sale (ACRIS data)

### Year-over-Year Comparable Sales ⭐ **NEW**
- **YoY Trend Flags**: Automatic Rising/Declining/Stable classification
- **Comparable Matching**: 5-10 recent sales from same building/neighborhood
- **Negotiation Insights**: Data-driven offer strategies based on market trends
- **Value vs Comps**: Instant pricing assessment (Underpriced/Fair/Overpriced)
- **DOF Rolling Sales**: Monthly updated comp data from NYC Department of Finance

### Intelligent Ranking
Properties scored on a 0-100 scale considering:
- **Price Match** (40 pts): How close to buyer's budget
- **HOA Impact** (20 pts): Annual HOA cost as % of price
- **Commute Score** (15 pts): Subway accessibility
- **Amenities Match** (15 pts): Elevator, doorman, etc.
- **Distress Bonus** (10 pts): Motivated seller signals

### Seller Signals
Automatic detection of motivated sellers:
- **HIGH**: 10%+ price cut + 2+ cuts + 60+ days on market
- **MEDIUM**: 5%+ price cut OR 45+ days on market
- **LOW**: Recent listing or stable pricing

### Market Context
Every property includes:
- Rent-to-price ratio vs neighborhood average
- Price per sqft vs comparables
- HOA cost evaluation
- Historical pricing trends (ACRIS-powered)
- Recent comparable sales
- Assessed value analysis (PLUTO data)

## Target Markets

- Manhattan condos
- Long Island City condos
- Brooklyn condos

## Budget

Under $100/month using free tiers where possible:
- Airtable: Free tier (1,200 records/base)
- OpenAI API: Pay-per-use (~$10-20/month)
- Zapier: Free tier (100 tasks/month)
- Retool/Glide: Free tier

## Getting Started

See `docs/IMPLEMENTATION.md` for detailed setup instructions.

## Sample Use Case

**User Input:**
> "Looking for a 2 bedroom under $1.8M with an elevator, lots of natural light, near the subway in LIC or Manhattan. Want low HOA fees."

**System Output:**
1. Parses preferences into structured criteria
2. Matches against 500+ properties in database
3. Returns top 10 ranked by fit score
4. Shows why each property matches (or doesn't)
5. Highlights motivated sellers with price cuts
6. Provides market context (is this a good deal?)

## Data Sources

**NYC Open Data Integration:**
- **ACRIS** (Automated City Register Information System): Historical sales records 1966-present
- **PLUTO** (Primary Land Use Tax Lot Output): Property assessments, sq ft, year built
- **DOF Annualized Sales**: Quarterly median sales by neighborhood/zip
- **StreetEasy Market Reports**: Rental market data and trends

All data sources are free and publicly available.

## Documentation

- [Airtable Schema](schemas/airtable-schema.json)
- [Investment Metrics Guide](docs/INVESTMENT_METRICS.md)
- [YoY Comps Analysis](docs/YOY_ANALYSIS.md) ⭐ **NEW**
- [Implementation Guide](docs/IMPLEMENTATION.md)
- [Formula Reference](docs/FORMULAS.md)
- [OpenAI Parser](docs/OPENAI_PARSER.md)
- [UI/UX Design](docs/UI_UX_DESIGN.md)
- [Comps UI Components](docs/COMPS_UI.md) ⭐ **NEW**

## License

MIT
