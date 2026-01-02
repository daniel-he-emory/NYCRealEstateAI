# Investment Valuation Metrics

Complete guide to the five priority investment metrics for NYC condo valuation, plus historical trend analysis.

## Overview

NYC condos have unique characteristics: low yields (2-3%), high appreciation potential, and high carrying costs. These metrics help investors quickly identify value opportunities beyond simple rent-to-price ratios.

---

## Priority Metric #1: Cap Rate (Capitalization Rate)

### Definition
Cap Rate measures the annual return on investment if you paid all cash, calculated as Net Operating Income divided by property price.

### Formula
```
Cap Rate = (NOI / Current Price) × 100

Where NOI = Annual Gross Rent - Annual Operating Expenses
```

### Airtable Implementation

**Step 1: Calculate Total Annual Expenses**
```
TotalAnnualExpenses = (MonthlyHOA × 12) + EstimatedAnnualTaxes + EstimatedInsurance + EstimatedUtilities + PropertyManagementFee
```

**Step 2: Calculate NOI**
```
NetOperatingIncome = AnnualRent - TotalAnnualExpenses
```

**Step 3: Calculate Cap Rate**
```
CapRate = IF(CurrentPrice > 0,
  ROUND(NetOperatingIncome / CurrentPrice * 100, 2),
  0
)
```

### NYC Benchmarks

| Cap Rate | Rating | Meaning |
|----------|--------|---------|
| >5% | Excellent | Rare in Manhattan, strong cash flow |
| 4-5% | Good | Above average for NYC condos |
| 3-4% | Fair | Typical Manhattan range |
| <3% | Poor | Appreciation play, negative cash flow likely |

**Manhattan Average**: 3.2%
**Queens/LIC Average**: 3.8%
**Brooklyn Average**: 3.5%

### Example
- **Property**: 2BR in LIC
- **Price**: $1,500,000
- **Annual Rent**: $66,000
- **Annual HOA**: $10,200
- **Annual Taxes**: $7,500
- **Insurance**: $1,200
- **Utilities**: $1,800
- **Total Expenses**: $20,700
- **NOI**: $66,000 - $20,700 = $45,300
- **Cap Rate**: $45,300 / $1,500,000 = **3.02%**

### Value Signals
- ✅ **Cap Rate > Neighborhood Average**: Better income potential
- ⚠️ **Cap Rate < 3%**: Likely negative cash flow with financing
- 🔥 **Cap Rate > 4% in Manhattan**: Rare opportunity, investigate

---

## Priority Metric #2: Price Per Square Foot (PPSF)

### Definition
The most common size-adjusted valuation metric. Allows comparing properties of different sizes.

### Formula
```
PPSF = Current Price / Square Footage
```

### Airtable Implementation
```
PricePerSQFT = IF(SQFT > 0,
  ROUND(CurrentPrice / SQFT, 2),
  0
)
```

### NYC Benchmarks (2025)

**Manhattan**:
- Luxury ($2,100+ /sqft): Upper East/West Side, Tribeca, Soho
- Mid-Market ($1,800-$2,100 /sqft): Most of Manhattan
- Value ($1,500-$1,800 /sqft): Upper Manhattan, some FiDi

**Queens/LIC**:
- High ($1,300+ /sqft): New waterfront towers
- Median ($1,100-$1,300 /sqft): Most LIC condos
- Value (<$1,100 /sqft): Older buildings, further from subway

**Brooklyn**:
- Premium ($1,600+ /sqft): DUMBO, Brooklyn Heights, Park Slope
- Median ($1,200-$1,600 /sqft): Most neighborhoods
- Value (<$1,200 /sqft): Outer Brooklyn

### Comparative Analysis
Always compare PPSF to:
1. **Building average** (same address, other units)
2. **Neighborhood median** (from Neighborhoods table)
3. **Historical average** (5-year trend)

### Value Signals
- ✅ **10%+ below neighborhood median**: Potential undervaluation
- ✅ **Below building average**: May indicate motivated seller or inferior unit
- ⚠️ **20%+ above median**: Overpriced unless justified (penthouse, renovation, etc.)

### Example
- **Property**: $1,650,000 / 1,250 sqft = **$1,320 /sqft**
- **LIC Median**: $1,180 /sqft
- **Analysis**: 12% premium likely due to high floor + south exposure (✓ Justified)

---

## Priority Metric #3: Gross Rent Multiplier (GRM)

### Definition
Fast screening tool showing how many years of rent equal the purchase price. Lower is better.

### Formula
```
GRM = Purchase Price / Annual Gross Rent
```

### Airtable Implementation
```
GrossRentMultiplier = IF(AnnualRent > 0,
  ROUND(CurrentPrice / AnnualRent, 1),
  0
)
```

### NYC Benchmarks

| GRM | Rating | Interpretation |
|-----|--------|----------------|
| <10x | Excellent | Rare in NYC, strong value |
| 10-12x | Good | Favorable for investors |
| 12-15x | Fair | Typical NYC range |
| >15x | Poor | Expensive relative to rent |

**Manhattan Average**: 14.2x
**Queens/LIC Average**: 12.5x
**Brooklyn Average**: 13.1x

### Why It Matters
- **Quick screening**: Calculate in 5 seconds (Price ÷ Annual Rent)
- **Relative comparison**: Compare across neighborhoods/building types
- **Investor lens**: Lower GRM = better for buy-and-hold investors

### Example
- **Price**: $1,500,000
- **Annual Rent**: $66,000
- **GRM**: $1,500,000 / $66,000 = **22.7x**
- **Analysis**: High GRM indicates appreciation play, not cash flow

### Value Signals
- ✅ **GRM < 12x in Manhattan**: Investigate opportunity
- ✅ **2-3 points below neighborhood average**: Strong relative value
- ⚠️ **GRM > 20x**: Negative cash flow almost certain

---

## Priority Metric #4: Cash-on-Cash Return

### Definition
Annual pre-tax cash flow as a percentage of your initial cash investment (down payment + closing costs).

### Formula
```
Cash-on-Cash Return = (Annual Cash Flow / Total Cash Invested) × 100

Where:
Annual Cash Flow = NOI - Annual Debt Service
Total Cash Invested = Down Payment + Closing Costs
```

### Airtable Implementation

**Step 1: Calculate Loan Amount**
```
LoanAmount = CurrentPrice - DownPayment
```

**Step 2: Calculate Monthly Payment** (mortgage formula)
```
MonthlyDebtService = IF(AND(LoanAmount > 0, InterestRate > 0, LoanTermYears > 0),
  LoanAmount * (InterestRate/12) * POWER(1 + InterestRate/12, LoanTermYears*12) /
  (POWER(1 + InterestRate/12, LoanTermYears*12) - 1),
  0
)
```

**Step 3: Calculate Annual Debt Service**
```
AnnualDebtService = MonthlyDebtService * 12
```

**Step 4: Calculate Cash Flow**
```
AnnualCashFlow = NetOperatingIncome - AnnualDebtService
```

**Step 5: Calculate Return**
```
CashOnCashReturn = IF(DownPayment > 0,
  ROUND(AnnualCashFlow / DownPayment * 100, 2),
  0
)
```

### Target Returns

| Return | Rating | Context |
|--------|--------|---------|
| >10% | Excellent | Very rare in NYC |
| 8-10% | Good | Strong leveraged return |
| 5-8% | Fair | Acceptable for stability + appreciation |
| 0-5% | Marginal | Appreciation bet |
| <0% | Negative | Requires cash injection monthly |

### Assumptions for NYC
- **Down payment**: 25% (typical for investment property)
- **Interest rate**: 7.0% (2025 rates)
- **Loan term**: 30 years
- **Closing costs**: 2-3% (not included in Airtable formula for simplicity)

### Example: LIC 2BR Investment Analysis

**Property Details**:
- Price: $1,500,000
- Down payment (25%): $375,000
- Loan: $1,125,000
- Interest: 7.0%
- Term: 30 years

**Income**:
- Annual Rent: $66,000

**Expenses**:
- HOA: $10,200/yr
- Taxes: $7,500/yr
- Insurance: $1,200/yr
- Utilities: $1,800/yr
- Management: $6,600/yr (10% of rent)
- **Total**: $27,300/yr

**Calculations**:
- NOI: $66,000 - $27,300 = **$38,700**
- Monthly Payment: $7,484
- Annual Debt: $89,808
- Cash Flow: $38,700 - $89,808 = **-$51,108**
- Cash-on-Cash: -$51,108 / $375,000 = **-13.6%**

**Conclusion**: Massive negative cash flow. This is an appreciation play, not an income property.

### Value Signals
- ✅ **Cash-on-Cash > 8%**: Strong income property
- ⚠️ **0-5%**: Breakeven to slight positive, appreciation dependent
- 🚫 **Negative**: Requires monthly subsidy (common in Manhattan)

---

## Priority Metric #5: Debt Service Coverage Ratio (DSCR)

### Definition
Ratio of Net Operating Income to annual debt payments. Measures ability to cover mortgage from rental income.

### Formula
```
DSCR = NOI / Annual Debt Service
```

### Airtable Implementation
```
DSCR = IF(AnnualDebtService > 0,
  ROUND(NetOperatingIncome / AnnualDebtService, 2),
  0
)
```

### Lending Standards

| DSCR | Loan Eligibility |
|------|------------------|
| >1.5x | Excellent - easy approval, best rates |
| 1.25-1.5x | Good - meets lender minimums |
| 1.0-1.25x | Marginal - may require higher down payment |
| <1.0x | Poor - rental income insufficient, loan denied |

**Minimum for most lenders**: 1.25x
**Preferred**: 1.4x+

### Why It Matters
- **Loan approval**: Lenders require DSCR >1.25 for investment property loans
- **Safety margin**: Higher DSCR = more cushion for vacancies, repairs
- **Refinance ability**: Low DSCR makes refinancing difficult

### Example (continuing LIC 2BR)
- NOI: $38,700
- Annual Debt: $89,808
- DSCR: $38,700 / $89,808 = **0.43x**

**Analysis**: Far below 1.25 minimum. Lender would reject loan based on rental income alone. Borrower must qualify based on personal income.

### NYC Reality
Most Manhattan condos have DSCR <1.0, meaning:
- Buyers qualify on W-2 income, not rental income
- Properties are purchased for appreciation, not cash flow
- Rent offsets carrying costs but doesn't fully cover them

### Value Signals
- ✅ **DSCR >1.25**: Qualifies for investment property loan
- ✅ **DSCR >1.0**: Rent covers mortgage (rare in Manhattan)
- ⚠️ **DSCR 0.8-1.0**: Manageable shortfall
- 🚫 **DSCR <0.8**: Large monthly subsidy required

---

## Historical Trend Analysis

### New Fields for Historical Valuation

Add these fields to track price trends over time:

1. **HistoricalPPSF_1YrAvg**: Average PPSF from sales 1 year ago
2. **HistoricalPPSF_3YrAvg**: Average PPSF from 3 years ago
3. **HistoricalPPSF_5YrAvg**: Average PPSF from 5 years ago
4. **PPSFChange5Yr**: % change vs 5-year average
5. **PPSFTrendFlag**: Undervalued/Stable/Overheated

### Formula: PPSF Trend Flag
```
PPSFTrendFlag = IF(PPSFChange5Yr < -5,
  'Undervalued',
  IF(PPSFChange5Yr > 10,
    'Overheated',
    'Stable'
  )
)
```

### Interpretation

**Undervalued** (Current PPSF >5% below 5-yr avg):
- Potential buy signal
- Market correction or property-specific issues
- Compare to neighborhood trends (is whole area down?)

**Stable** (-5% to +10%):
- Normal market conditions
- Price aligned with historical norms

**Overheated** (Current PPSF >10% above 5-yr avg):
- Potential bubble territory
- Seller's market dynamics
- Consider waiting or negotiating

### Example
- **Current PPSF**: $1,320
- **5-Year Average**: $1,505
- **Change**: ($1,320 - $1,505) / $1,505 = **-12.3%**
- **Flag**: **Undervalued** 🔥

**Analysis**: Property is 12% below historical average. Potential buy signal if:
1. Neighborhood trend is similar (market-wide correction = normal)
2. Building/unit fundamentals haven't changed
3. No major defects or issues

If neighborhood is only down 3%, investigate property-specific reasons for discount.

---

## Assessed Value Ratio (AVR)

### Definition
Ratio of market price to NYC Department of Finance assessed value. Helps identify undervaluation.

### Formula
```
AVR = Market Price / DOF Assessed Value
```

### Data Source
NYC PLUTO dataset (free, updated annually):
- Download: https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page
- Contains: Assessed values, lot sizes, building classes

### NYC Assessment Context
- **Class 2 (Residential 4+ units)**: Assessed at ~45% of market value
- **Class 4 (Commercial + large residential)**: Assessed at ~45% of market value
- Assessment lags market by 1-3 years (conservative valuations)

### Benchmarks

| AVR | Interpretation |
|-----|----------------|
| >2.5 | Property priced well above assessed value (market-driven premium) |
| 2.0-2.5 | Normal range for NYC condos |
| 1.5-2.0 | Moderate potential undervaluation |
| <1.5 | Significant undervaluation signal OR recent assessment increase |

### Example
- **Market Price**: $1,500,000
- **Assessed Value**: $680,000 (from PLUTO)
- **AVR**: $1,500,000 / $680,000 = **2.21**

**Analysis**: Within normal range. Market price is 2.2x assessed value, typical for NYC condos.

### Value Signal
- ✅ **AVR 1.5-1.9**: Investigate potential value opportunity
- ⚠️ **AVR >3.0**: Market price significantly exceeds assessment (verify pricing)

---

## Investment Grade System

### Composite Scoring
Combine all metrics into an overall Investment Grade (A-D):

**Grade A** (Best):
- Cap Rate ≥ 4%
- GRM ≤ 12x
- Cash-on-Cash ≥ 8%
- DSCR ≥ 1.25

**Grade B** (Good):
- Cap Rate ≥ 3%
- GRM ≤ 15x
- Cash-on-Cash ≥ 5%
- DSCR ≥ 1.0

**Grade C** (Fair):
- Cap Rate ≥ 2%
- GRM ≤ 18x
- Cash-on-Cash > 0%

**Grade D** (Poor):
- Below Grade C thresholds

### Airtable Formula
```
InvestmentGrade = IF(
  AND(CapRate >= 4, GrossRentMultiplier <= 12, CashOnCashReturn >= 8, DSCR >= 1.25),
  'A',
  IF(
    AND(CapRate >= 3, GrossRentMultiplier <= 15, CashOnCashReturn >= 5, DSCR >= 1.0),
    'B',
    IF(CapRate >= 2, 'C', 'D')
  )
)
```

### Reality Check: Manhattan Grades
**Typical Manhattan condo**: Grade C or D
- Why? Low cap rates (2-3%), high GRMs (14-18x), negative cash flow

**This is normal** - Manhattan investing is about:
1. **Appreciation**: 3-5% annual price growth
2. **Rent subsidy**: Rent offsets 50-70% of carrying costs
3. **Tax benefits**: Depreciation, mortgage interest deductions
4. **Leverage**: 4:1 leverage amplifies appreciation

**Grade A/B properties** in NYC:
- Usually in outer boroughs (Queens, Brooklyn, Bronx)
- Older buildings (lower HOA)
- Smaller units (better rent-to-price)
- Cash flow oriented investors

---

## Data Sources for Auto-Population

### 1. ACRIS (Automated City Register Information System)
**What**: NYC deed sales records since 1966
**URL**: https://a836-acris.nyc.gov/
**Data**: Sale prices, dates, document IDs
**Use**: Populate LastSalePrice, LastSaleDate, historical PPSF

**CSV Export**:
```python
# Via NYC Open Data API
import requests

url = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"
params = {
    "address": "4610 CENTER BLVD",
    "borough": "QUEENS",
    "$limit": 10,
    "$$app_token": "YOUR_TOKEN"
}
response = requests.get(url, params=params)
sales = response.json()
```

### 2. PLUTO (Primary Land Use Tax Lot Output)
**What**: Property-level data for every tax lot in NYC
**URL**: https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page
**Data**: Assessed values, sq ft, year built, zoning
**Use**: Populate AssessedValue, YearBuilt, SQFT verification

**Download**: Annual CSV/Shapefile release (1GB+)

### 3. DOF Annualized Sales
**What**: Quarterly median sales by neighborhood/zip
**URL**: https://www.nyc.gov/site/finance/taxes/property-annualized-sales-update.page
**Data**: Median prices, sales volume, PPSF by zip code
**Use**: Populate Neighborhoods table with quarterly trends

### 4. StreetEasy Market Reports
**What**: Rental market data by neighborhood
**URL**: https://streeteasy.com/blog/data-dashboard/
**Data**: Median rents, inventory, absorption
**Use**: Populate EstimatedMonthlyRent, verify market rents

---

## Implementation Checklist

### Phase 1: Add Fields to Airtable
- [ ] Add expense fields (taxes, insurance, utilities, management)
- [ ] Add financing fields (down payment, interest rate, loan term)
- [ ] Add formula fields for NOI, Cap Rate, GRM, Cash-on-Cash, DSCR
- [ ] Add historical PPSF fields (1yr, 3yr, 5yr averages)
- [ ] Add AssessedValue field
- [ ] Add InvestmentGrade formula field

### Phase 2: Populate Historical Data
- [ ] Download ACRIS sales data for target neighborhoods
- [ ] Download PLUTO dataset
- [ ] Create Python script to populate historical PPSF averages
- [ ] Import assessed values from PLUTO
- [ ] Verify data accuracy with spot checks

### Phase 3: Create Views
- [ ] "Top Investment Opportunities" (Grade A/B only)
- [ ] "High Cap Rate (>4%)"
- [ ] "Positive Cash Flow"
- [ ] "Undervalued (PPSF Trend)"
- [ ] "Low GRM (<12x)"

### Phase 4: Update UI
- [ ] Add investment metrics to property detail screen
- [ ] Create comparison charts (property vs neighborhood avg)
- [ ] Add grade badges (A/B/C/D) to property cards
- [ ] Show "Value Signals" based on metric thresholds

### Phase 5: Documentation
- [ ] Update README with investment focus
- [ ] Create investor guide explaining each metric
- [ ] Add case studies (sample properties with full analysis)
- [ ] Document data source update procedures

---

## Example: Complete Property Analysis

### Property: 4610 Center Blvd #1234, LIC

**Basic Info**:
- Price: $1,650,000
- SQFT: 1,250
- Bedrooms: 2
- Bathrooms: 2

**Income**:
- Estimated Rent: $5,200/mo ($62,400/yr)

**Expenses**:
- HOA: $850/mo ($10,200/yr)
- Taxes: $8,250/yr (0.5% of price)
- Insurance: $1,200/yr
- Utilities: $1,800/yr
- Management: $6,240/yr (10% of rent)
- **Total**: $27,690/yr

**Financing** (25% down, 7%, 30yr):
- Down Payment: $412,500
- Loan: $1,237,500
- Monthly Payment: $8,232
- Annual Debt: $98,784

**Metrics**:
- **PPSF**: $1,320 (vs LIC median $1,180 = +12%)
- **NOI**: $62,400 - $27,690 = $34,710
- **Cap Rate**: $34,710 / $1,650,000 = **2.1%** (Fair)
- **GRM**: $1,650,000 / $62,400 = **26.4x** (Poor)
- **Cash Flow**: $34,710 - $98,784 = **-$64,074/yr**
- **Cash-on-Cash**: -$64,074 / $412,500 = **-15.5%** (Negative)
- **DSCR**: $34,710 / $98,784 = **0.35** (Well below 1.25 minimum)

**Investment Grade**: **D**

**Conclusion**:
This is NOT a cash flow investment. It's a **$5,340/month negative cash flow** property. However, if buyer expects:
- 4% annual appreciation = $66,000/yr gain
- Tax benefits = ~$15,000/yr (depreciation + mortgage interest)
- Total economic benefit = $81,000 - $64,000 = $17,000/yr
- True return on $412,500 equity = 4.1%

**Who should buy?**
- W-2 earners who can cover monthly shortfall
- Believers in LIC long-term appreciation
- Tax-motivated buyers (high income, need deductions)

**Who should avoid?**
- Cash flow investors
- First-time investors
- Anyone unable to cover $5K+/month gap

---

## Neighborhood Benchmarks Summary

| Metric | Manhattan | LIC/Queens | Brooklyn |
|--------|-----------|-----------|----------|
| **Cap Rate** | 2.8-3.5% | 3.2-4.2% | 3.0-3.8% |
| **PPSF** | $1,800-2,100 | $1,100-1,400 | $1,200-1,600 |
| **GRM** | 13-16x | 11-14x | 12-15x |
| **Rent-to-Price** | 2.5-3.5% | 3.0-4.5% | 2.8-4.0% |

**Key Insight**: Outer borough properties (Queens, Brooklyn) generally offer better cash flow metrics but lower appreciation potential than Manhattan.

---

## Next Steps

1. Implement all new fields in Airtable (see `investment-metrics-fields.json`)
2. Create Python script to pull ACRIS/PLUTO data
3. Build automated data refresh pipeline
4. Add investment metrics to UI
5. Create investor-focused marketing materials

This transforms NYCRealEstateAI from a search tool into a **complete investment analysis platform**.
