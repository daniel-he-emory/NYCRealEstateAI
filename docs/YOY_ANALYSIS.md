# Year-over-Year Comparable Sales Analysis

Complete guide to the YoY valuation system for NYCRealEstateAI, using DOF Rolling Sales and ACRIS data to identify market trends and negotiation opportunities.

## Overview

Year-over-year (YoY) analysis tracks how comparable properties have appreciated or depreciated over the past 12 months, providing critical market intelligence for:

1. **Buyers**: Identify declining markets for better negotiation leverage
2. **Investors**: Spot rising markets for appreciation potential
3. **Sellers**: Price competitively based on recent trend data
4. **Agents**: Provide data-driven market insights

---

## System Architecture

### Data Flow

```
DOF Rolling Sales (Excel)
         ↓
   Parse & Filter
         ↓
ComparableSales Table
         ↓
  Calculate YoY Change
         ↓
  Link to Properties
         ↓
AvgCompsYoY_PPSF Rollup
         ↓
   YoYTrendFlag
```

### Key Components

1. **ComparableSales Table**: Stores individual comp sales with YoY calculations
2. **Properties Table Rollups**: Aggregates comp data (avg YoY, median PPSF, count)
3. **YoY Formulas**: Auto-calculate percentage changes
4. **Trend Flags**: Classify markets as Rising/Declining/Stable
5. **Data Loader Script**: Automated fetching from DOF/ACRIS

---

## ComparableSales Table

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| **BBL** | Text | 10-digit Borough-Block-Lot identifier |
| **Address** | Text | Full property address |
| **Bedrooms** | Number | Number of bedrooms |
| **SQFT** | Number | Square footage |
| **SaleDate** | Date | Date of sale closing |
| **SalePrice** | Currency | Recorded sale price |
| **PPSF** | Formula | SalePrice / SQFT |
| **PriorYearSalePrice** | Currency | Sale price from 12 months prior |
| **PriorYearPPSF** | Formula | Prior year price per sqft |
| **YoY_PPSF_Change** | Formula | Percentage change year-over-year |
| **PropertyLink** | Link | Link to active listing if applicable |

### YoY Calculation Formula

```
YoY_PPSF_Change = IF(PriorYearPPSF > 0,
  ROUND((PPSF - PriorYearPPSF) / PriorYearPPSF * 100, 2),
  0
)
```

**Example**:
- Current sale: Dec 2024, $1,650,000, 1,200 sqft = **$1,375/sqft**
- Prior year sale: Nov 2023, $1,550,000, 1,200 sqft = **$1,292/sqft**
- YoY Change: (1375 - 1292) / 1292 × 100 = **+6.4%**

---

## Properties Table Enhancements

### New Fields

#### 1. ComparableSales (Link)
- **Type**: Link to another record (multiple)
- **Links to**: ComparableSales table
- **Purpose**: Connect property to its comps

#### 2. CompsCount (Rollup)
```
Type: Rollup
Linked field: ComparableSales
Rollup field: CompID
Aggregation: COUNTA
```
- **Purpose**: Count number of comps (need ≥3 for validity)
- **Signal**: <3 comps = "Insufficient Data" flag

#### 3. AvgCompsYoY_PPSF (Rollup)
```
Type: Rollup
Linked field: ComparableSales
Rollup field: YoY_PPSF_Change
Aggregation: AVERAGE
```
- **Purpose**: Average YoY change across all comps
- **Example**: Property with 5 comps showing +2%, +3%, +1%, +4%, +2% = Avg **+2.4%**

#### 4. MedianCompsPPSF (Rollup)
```
Type: Rollup
Linked field: ComparableSales
Rollup field: PPSF
Aggregation: MEDIAN
```
- **Purpose**: Median PPSF of recent comps
- **Use**: Compare listing price to recent sales

#### 5. YoYTrendFlag (Formula)
```
YoYTrendFlag = IF(CompsCount < 3,
  'Insufficient Data',
  IF(AvgCompsYoY_PPSF > 5,
    'Rising',
    IF(AvgCompsYoY_PPSF < -5,
      'Declining',
      'Stable'
    )
  )
)
```

**Classification**:
- **Rising**: >5% avg YoY (hot market, limited negotiation)
- **Declining**: <-5% avg YoY (buyer's market, strong negotiation leverage)
- **Stable**: -5% to +5% (normal market)
- **Insufficient Data**: <3 comps

#### 6. CompsPriceVariance (Formula)
```
CompsPriceVariance = IF(
  AND(MedianCompsPPSF > 0, PricePerSQFT > 0),
  ROUND((PricePerSQFT - MedianCompsPPSF) / MedianCompsPPSF * 100, 2),
  0
)
```

**Purpose**: How current listing compares to recent comps

**Example**:
- Listing PPSF: $1,320
- Median Comp PPSF: $1,400
- Variance: (1320 - 1400) / 1400 = **-5.7%**
- Signal: **Underpriced** (good value)

#### 7. ValueVsComps (Formula)
```
ValueVsComps = IF(CompsPriceVariance < -10,
  'Underpriced',
  IF(CompsPriceVariance > 10,
    'Overpriced',
    'Fair'
  )
)
```

---

## Comparable Matching Logic

### Priority 1: Same Building (Excellent Comps)
**Criteria**:
- Same building address (BBL first 6 digits match)
- Beds within ±1
- SQFT within ±20%
- Sale within last 24 months

**Quality**: Excellent

**Example**:
- Property: 4610 Center Blvd #12A, 2BR, 1,200 sqft
- Comp: 4610 Center Blvd #8B, 2BR, 1,150 sqft, sold Nov 2024

### Priority 2: Same Zip Code (Good Comps)
**Criteria**:
- Same zip code
- Same number of bedrooms
- SQFT within ±15%
- Sale within last 18 months

**Quality**: Good

### Priority 3: Same Neighborhood (Fair Comps)
**Criteria**:
- Same neighborhood (from Neighborhoods table)
- Beds within ±1
- SQFT within ±25%
- Sale within last 12 months

**Quality**: Fair

### Minimum Requirements
- **Ideal**: 5-10 comps per property
- **Minimum**: 3 comps for valid analysis
- **Max age**: 24 months
- **Arms-length only**: Exclude family transfers, bulk sales, outliers

---

## Data Sources

### NYC DOF Rolling Sales

**What**: Excel files updated monthly with recent condo/co-op sales
**URL**: https://www.nyc.gov/site/finance/taxes/property-rolling-sales-data.page
**Coverage**: Last ~12 months of sales
**Format**: Excel (.xlsx) with standardized columns

**Key Columns**:
- BOROUGH
- NEIGHBORHOOD
- BUILDING CLASS CATEGORY (filter for "CONDO")
- ADDRESS
- ZIP CODE
- RESIDENTIAL UNITS
- GROSS SQUARE FEET
- YEAR BUILT
- SALE PRICE
- SALE DATE

**Download URLs** (automated in script):
```python
{
  "Manhattan": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xlsx",
  "Brooklyn": "...rollingsales_brooklyn.xlsx",
  "Queens": "...rollingsales_queens.xlsx",
  "Bronx": "...rollingsales_bronx.xlsx",
  "Staten Island": "...rollingsales_statenisland.xlsx"
}
```

### ACRIS (Historical Baseline)

**What**: Complete deed records since 1966
**Use**: Find prior year sales for YoY calculation
**API**: NYC Open Data Socrata
**Dataset ID**: bnx9-e6tj

**Query Example**:
Find sales at BBL 1-00123-4567 between Nov 2023 - Jan 2024:
```python
results = client.get(
    "bnx9-e6tj",
    where="borough='1' AND document_date BETWEEN '2023-11-01' AND '2024-01-31'",
    limit=100
)
```

---

## YoY Calculation Methodology

### Step-by-Step Process

#### Step 1: Identify Comparable Sale
- Address: 4610 Center Blvd #12B
- Sale Date: Dec 15, 2024
- Sale Price: $1,650,000
- SQFT: 1,200
- PPSF: $1,375

#### Step 2: Find Prior Year Baseline

**Option A**: Same Unit Sale (Best)
- Query ACRIS for sales at exact same unit 12-18 months prior
- Example: #12B sold Nov 20, 2023 for $1,550,000 = $1,292/sqft

**Option B**: Same Building Average (Good)
- If no exact unit match, find all sales in building from 12-18 months prior
- Calculate median PPSF of similar units (same bed count)
- Example: 3 sales in building avg $1,300/sqft

**Option C**: Neighborhood Median (Fair)
- If <3 building sales, use neighborhood median from that period
- Less reliable but provides baseline

#### Step 3: Calculate YoY Change
```
YoY % = (Current PPSF - Prior PPSF) / Prior PPSF × 100
YoY % = (1375 - 1292) / 1292 × 100 = +6.4%
```

#### Step 4: Aggregate to Property Level
For property listing at 4610 Center Blvd #15C:
- Find all comps in same building
- Calculate YoY for each comp
- Average: (6.4% + 5.1% + 7.2% + 4.8%) / 4 = **5.9% avg**
- Flag: **"Rising"** market

---

## Example Analysis

### Property: 4610 Center Boulevard #15C, LIC

**Basic Info**:
- Listed: $1,800,000
- SQFT: 1,300
- PPSF: $1,385
- Beds: 2BR

**Comparable Sales** (last 12 months):

| Unit | Sale Date | Price | SQFT | PPSF | YoY Change | Quality |
|------|-----------|-------|------|------|-----------|---------|
| #12B | Dec 2024 | $1.65M | 1,200 | $1,375 | +6.4% | Excellent |
| #8B | Nov 2024 | $1.55M | 1,150 | $1,348 | +5.1% | Excellent |
| #20A | Oct 2024 | $1.72M | 1,250 | $1,376 | +7.2% | Excellent |
| #6D | Sep 2024 | $1.48M | 1,180 | $1,254 | +4.8% | Excellent |
| #18C | Aug 2024 | $1.62M | 1,220 | $1,328 | +3.9% | Excellent |

**Aggregated Metrics**:
- **CompsCount**: 5
- **MedianCompsPPSF**: $1,348
- **AvgCompsYoY_PPSF**: +5.5%
- **YoYTrendFlag**: **Rising**
- **CompsPriceVariance**: (1385 - 1348) / 1348 = **+2.7%**
- **ValueVsComps**: **Fair** (within ±10%)

**Interpretation**:

✅ **Market Trend**: Rising market (+5.5% YoY) - prices appreciating
✅ **Pricing**: Listed 2.7% above median comps - fair pricing
✅ **Comps Quality**: 5 excellent comps (same building)
⚠️ **Negotiation**: Limited leverage in rising market, but not overheated

**Buyer Strategy**:
- Offer at or slightly below ask
- Emphasize any price cuts from comps
- If property has been on market >60 days, use that as leverage
- Consider quick close to lock in before further appreciation

---

## Views & Reports

### View 1: YoY Declining Comps
**Purpose**: Find negotiation opportunities

**Filter**:
```
AND(
  AvgCompsYoY_PPSF < -2,
  CompsCount >= 3,
  Status = 'Active'
)
```

**Sort**: AvgCompsYoY_PPSF ascending

**Use Case**: Properties in declining markets = strong buyer leverage

**Example Output**:
| Address | Avg YoY | Comps | Current PPSF | Median Comp | Variance |
|---------|---------|-------|--------------|-------------|----------|
| 100 Jay St #15A | -4.2% | 6 | $1,295 | $1,340 | -3.4% |
| 221 W 77th #4E | -3.8% | 5 | $1,625 | $1,680 | -3.3% |

### View 2: Rising Market Buildings
**Purpose**: Identify appreciation opportunities

**Filter**:
```
AND(
  AvgCompsYoY_PPSF > 5,
  CompsCount >= 3,
  Status = 'Active'
)
```

**Sort**: AvgCompsYoY_PPSF descending

**Use Case**: Hot markets for investment/quick appreciation

### View 3: Underpriced vs Comps
**Purpose**: Find value opportunities

**Filter**:
```
AND(
  ValueVsComps = 'Underpriced',
  CompsCount >= 3,
  Status = 'Active'
)
```

**Sort**: CompsPriceVariance ascending

**Use Case**: Properties priced 10%+ below recent sales

---

## Implementation Checklist

### Phase 1: Airtable Setup (1 hour)
- [ ] Create ComparableSales table
- [ ] Add all fields from `comps-fields.json`
- [ ] Add rollup fields to Properties table
- [ ] Create formula fields (YoYTrendFlag, ValueVsComps)
- [ ] Create 7 new views

### Phase 2: Data Loading (2-3 hours)
- [ ] Install dependencies: `pip install pandas openpyxl pyairtable sodapy`
- [ ] Configure API keys in `.env`
- [ ] Run: `python rolling_comps_loader.py --borough Manhattan`
- [ ] Verify data loaded correctly
- [ ] Run for Brooklyn, Queens
- [ ] Link properties to comps: `python rolling_comps_loader.py --link`

### Phase 3: YoY Calculation (Advanced)
- [ ] Implement ACRIS prior year lookup (requires BBL join)
- [ ] Calculate building-level YoY baselines
- [ ] Update PriorYearSalePrice for all comps
- [ ] Verify YoY formulas calculate correctly

### Phase 4: UI Integration
- [ ] Add comps table to property detail screen
- [ ] Show YoY trend badge
- [ ] Display sparkline of PPSF trend
- [ ] Add negotiation insights based on YoY

---

## Data Quality & Validation

### Exclude These Sales
- Sale price < $100,000 (likely non-arms-length)
- Sale price > $50M (outliers)
- PPSF < $200 or > $5,000 (data errors)
- SaleType = "Family Transfer" or "Bulk Sale"
- First sales in new development (use 2nd sale onwards)

### Quality Checks
- **Minimum 3 comps** per property for valid analysis
- **Max 24 months** old for comp relevance
- **SQFT variance** <25% for comparability
- **Bedroom match** ±1 for similarity

### Red Flags
- Property shows "Rising" but listed >90 days = overpriced
- Property shows "Declining" but priced above median comps = unrealistic seller
- <3 comps = need more data before conclusions

---

## Advanced: Seasonal Adjustments

NYC real estate has seasonal patterns:
- **Spring (Mar-May)**: Peak season, +5-8% premium
- **Summer (Jun-Aug)**: Active, normal pricing
- **Fall (Sep-Nov)**: Second peak, +3-5% premium
- **Winter (Dec-Feb)**: Slow, -5-10% discount

**Adjustment Formula** (optional):
```
Seasonally Adjusted YoY = Raw YoY - Seasonal Factor
```

Example:
- Comp sold in May 2024 vs May 2023: +8% YoY
- Seasonal factor: +6% (spring premium both years)
- Adjusted YoY: +8% - 6% = **+2%** (true appreciation)

---

## API Integration Examples

### Fetch Latest Rolling Sales
```python
loader = RollingCompsLoader()
loader.load_comps_for_borough("Manhattan", months_back=12)
```

### Link Properties to Comps
```python
loader.link_properties_to_comps()
```

### Query Properties by YoY Trend
```python
declining_props = properties_table.all(
    formula="AND({YoYTrendFlag}='Declining', {CompsCount} >= 3)"
)

for prop in declining_props:
    address = prop['fields']['Address']
    yoy = prop['fields']['AvgCompsYoY_PPSF']
    print(f"{address}: {yoy:.1f}% YoY decline")
```

---

## Troubleshooting

### Issue: No comps found for property
**Cause**: Unique property or new building
**Solution**: Expand search radius to neighborhood level

### Issue: YoY values showing 0%
**Cause**: No PriorYearSalePrice populated
**Solution**: Run ACRIS lookup or use building-level baseline

### Issue: CompsCount = 1 or 2
**Cause**: Strict matching criteria
**Solution**: Relax SQFT tolerance from 15% to 25%, expand date range to 24 months

### Issue: Conflicting YoY trends
**Cause**: Mix of excellent and fair quality comps
**Solution**: Filter to "Excellent" quality only for more accurate signal

---

## Next Steps

1. **Implement full ACRIS integration** for precise YoY baselines
2. **Add seasonal adjustments** for more accurate trend signals
3. **Create automated alerts** when comps show >5% decline (negotiation opportunities)
4. **Build predictive model** using YoY trends to forecast future appreciation
5. **Integrate with BuyerFitScore** to boost properties in declining markets

This YoY analysis transforms NYCRealEstateAI into a **market timing tool**, giving buyers and investors an edge through data-driven trend identification.
