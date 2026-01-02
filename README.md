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
- Historical pricing trends
- Recent comparable sales

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

## Documentation

- [Airtable Schema](schemas/airtable-schema.json)
- [Implementation Guide](docs/IMPLEMENTATION.md)
- [Formula Reference](docs/FORMULAS.md)
- [API Integration](docs/API.md)

## License

MIT
