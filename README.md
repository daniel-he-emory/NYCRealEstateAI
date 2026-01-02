# NYC Real Estate AI Recommendation System

A no-code/low-code intelligent property recommendation system that uses natural language processing to match buyers with properties based on sophisticated ranking algorithms, seller signals, and market context.

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
- [Investment Metrics Guide](docs/INVESTMENT_METRICS.md) ⭐ **NEW**
- [Implementation Guide](docs/IMPLEMENTATION.md)
- [Formula Reference](docs/FORMULAS.md)
- [OpenAI Parser](docs/OPENAI_PARSER.md)
- [UI/UX Design](docs/UI_UX_DESIGN.md)

## License

MIT
