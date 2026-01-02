# Airtable Formula Reference

This document provides all formulas used in the NYC Real Estate AI system with explanations and implementation notes.

## Properties Table Formulas

### 1. PriceCutCount
**Purpose**: Count how many times the price has been reduced

**Formula**:
```
IF(PriceHistory,
  LEN(PriceHistory) - LEN(SUBSTITUTE(PriceHistory, '},{', '}')),
  0
)
```

**How it works**: Counts occurrences of `},{` pattern in the PriceHistory JSON array to determine number of price changes.

**Example**:
- PriceHistory: `[{"date":"2024-01-15","price":1800000},{"date":"2024-02-01","price":1750000},{"date":"2024-03-01","price":1700000}]`
- Result: 2 price cuts

---

### 2. TotalCutPercent
**Purpose**: Calculate total percentage reduction from original listing price

**Formula**:
```
IF(
  AND(OriginalPrice > 0, CurrentPrice > 0),
  ROUND((OriginalPrice - CurrentPrice) / OriginalPrice * 100, 2),
  0
)
```

**How it works**: Computes percentage decrease, rounded to 2 decimals.

**Example**:
- Original: $1,800,000
- Current: $1,650,000
- Result: 8.33%

---

### 3. PricePerSQFT
**Purpose**: Calculate price per square foot

**Formula**:
```
IF(SQFT > 0,
  ROUND(CurrentPrice / SQFT, 2),
  0
)
```

**How it works**: Divides current price by square footage, with zero-division protection.

**Example**:
- Price: $1,500,000
- SQFT: 1,200
- Result: $1,250/sqft

---

### 4. HOAPercentOfPrice
**Purpose**: Calculate annual HOA fees as percentage of property price

**Formula**:
```
IF(CurrentPrice > 0,
  ROUND((MonthlyHOA * 12) / CurrentPrice * 100, 2),
  0
)
```

**How it works**: Annualizes monthly HOA, divides by price, converts to percentage.

**Evaluation Guide**:
- **Excellent**: < 1.5%
- **Good**: 1.5% - 2.5%
- **Fair**: 2.5% - 3.5%
- **Poor**: > 3.5%

**Example**:
- Price: $1,500,000
- Monthly HOA: $900
- Annual HOA: $10,800
- Result: 0.72% (Excellent)

---

### 5. RentToPriceRatio
**Purpose**: Calculate gross rental yield (cap rate proxy)

**Formula**:
```
IF(CurrentPrice > 0,
  ROUND((EstimatedMonthlyRent * 12) / CurrentPrice * 100, 2),
  0
)
```

**How it works**: Annual rent divided by purchase price as percentage.

**Market Context**:
- **High Yield**: ≥ 4.0% (investor-friendly)
- **Average**: 3.0% - 4.0%
- **Low Yield**: < 3.0% (expensive relative to rent)

**Example**:
- Price: $1,500,000
- Monthly Rent: $5,500
- Annual Rent: $66,000
- Result: 4.4% (High Yield)

---

### 6. DistressFlag
**Purpose**: Identify motivated sellers based on price cuts and time on market

**Formula**:
```
IF(
  AND(TotalCutPercent >= 10, PriceCutCount >= 2, DaysOnMarket >= 60),
  'High',
  IF(
    OR(TotalCutPercent >= 5, PriceCutCount >= 1, DaysOnMarket >= 45),
    'Medium',
    'Low'
  )
)
```

**Logic**:

**HIGH Distress** (all conditions must be true):
- Price cut ≥ 10% from original
- At least 2 separate price reductions
- On market ≥ 60 days

**MEDIUM Distress** (any condition true):
- Price cut ≥ 5%
- At least 1 price reduction
- On market ≥ 45 days

**LOW Distress**:
- None of the above conditions met

**Interpretation**:
- **High**: Seller likely highly motivated, good negotiation opportunity
- **Medium**: Some urgency, moderate negotiation potential
- **Low**: Fresh listing or stable pricing, less negotiation room

---

### 7. BuildingAge
**Purpose**: Calculate current age of building

**Formula**:
```
YEAR(TODAY()) - YearBuilt
```

**Example**:
- YearBuilt: 1985
- Today: 2025
- Result: 40 years old

---

### 8. AppreciationSinceLastSale
**Purpose**: Calculate price change since last recorded sale

**Formula**:
```
IF(
  AND(LastSalePrice > 0, CurrentPrice > 0),
  ROUND((CurrentPrice - LastSalePrice) / LastSalePrice * 100, 2),
  0
)
```

**Use Case**: Identify flips or understand seller's potential profit/loss

**Example**:
- Last Sale (2020): $1,200,000
- Current Price: $1,500,000
- Result: 25% appreciation

---

## BuyerFitScore Algorithm

**Purpose**: Rank properties 0-100 based on how well they match buyer preferences

### Full Scoring Formula

This is implemented as a computed field via automation (too complex for Airtable formula), but the logic is:

```javascript
// Price Match Component (40 points max)
const priceScore = (() => {
  if (currentPrice > userMaxPrice) return 0;
  const utilizationRatio = currentPrice / userMaxPrice;
  // Reward staying under budget, with best score around 80-90% of max
  if (utilizationRatio <= 0.85) return 40;
  return 40 * (1 - utilizationRatio);
})();

// HOA Impact (20 points max - lower HOA = higher score)
const hoaScore = (() => {
  const hoaPercent = property.HOAPercentOfPrice;
  if (hoaPercent <= 1.5) return 20;      // Excellent
  if (hoaPercent <= 2.5) return 15;      // Good
  if (hoaPercent <= 3.5) return 10;      // Fair
  return 5;                               // Poor
})();

// Commute Score (15 points max)
const commuteScore = (() => {
  const minutes = property.SubwayDistance;
  if (minutes <= 5) return 15;           // Excellent
  if (minutes <= 10) return 10;          // Good
  if (minutes <= 15) return 5;           // Acceptable
  return 0;                               // Too far
})();

// Amenities Match (15 points max)
const amenitiesScore = (() => {
  let score = 0;
  const weights = {
    HasElevator: 7.5,
    HasDoorman: 7.5,
    HasParking: 5,
    HasGym: 3,
    HasRoofDeck: 2,
    PetFriendly: 3
  };

  for (const [amenity, points] of Object.entries(weights)) {
    if (userRequires(amenity) && property[amenity]) {
      score += points;
    }
  }

  return Math.min(score, 15); // Cap at 15
})();

// Distress Bonus (10 points max - motivated sellers)
const distressScore = (() => {
  if (property.DistressFlag === 'High') return 10;
  if (property.DistressFlag === 'Medium') return 5;
  return 0;
})();

// Exposure/Light Bonus (5 points max)
const exposureScore = (() => {
  const preferred = ['South', 'Corner', 'Multiple'];
  if (preferred.includes(property.Exposure)) return 5;
  return 0;
})();

// Total Score
const buyerFitScore = priceScore + hoaScore + commuteScore +
                      amenitiesScore + distressScore + exposureScore;

return Math.min(Math.max(buyerFitScore, 0), 100); // Clamp 0-100
```

### Score Interpretation

| Score Range | Rating | Meaning |
|-------------|---------|---------|
| 90-100 | Excellent | Near-perfect match, highly recommended |
| 80-89 | Very Good | Strong match with minor compromises |
| 70-79 | Good | Solid option, some trade-offs |
| 60-69 | Fair | Acceptable but notable gaps |
| 50-59 | Below Average | Marginal fit, consider alternatives |
| < 50 | Poor | Significant mismatches |

### Component Weights Rationale

1. **Price (40%)**: Largest factor - staying within budget is critical
2. **HOA (20%)**: Ongoing cost impacts affordability significantly
3. **Commute (15%)**: Daily quality of life factor
4. **Amenities (15%)**: Nice-to-haves that add value
5. **Distress (10%)**: Bonus for negotiation opportunity

---

## Neighborhoods Table Formulas

### RentToPriceRatio (Neighborhood Average)
```
IF(MedianPrice > 0,
  ROUND((MedianRent * 12) / MedianPrice * 100, 2),
  0
)
```

Same logic as property-level, but uses neighborhood medians.

---

## HistoricalSales Table Formulas

### PricePerSQFT (Historical)
```
IF(SQFT > 0,
  ROUND(SalePrice / SQFT, 2),
  0
)
```

Used to compare current listings against actual sold prices.

---

## Implementation Notes

### For Airtable:
1. All formulas use field names exactly as defined in schema
2. Currency fields automatically format with $ symbol
3. Percent fields display with % symbol
4. Use `ROUND(value, 2)` for all currency/percent calculations

### For BuyerFitScore Automation:
Since Airtable formulas can't reference user preferences dynamically, implement this as:
- **Option 1**: Zapier/Make automation that runs when a search is created
- **Option 2**: Retool scripting when displaying results
- **Option 3**: Airtable script automation triggered on search

**Recommended**: Zapier workflow:
1. Trigger: New record in BuyerSearches
2. Action: Run JavaScript to calculate scores for all matching properties
3. Action: Update BuyerFitScore field for each property

---

## Testing Your Formulas

### Sample Data for Testing

**Property A** (Should score HIGH for distress):
- OriginalPrice: $2,000,000
- CurrentPrice: $1,700,000
- DaysOnMarket: 75
- PriceCutCount: 3
- Expected DistressFlag: High
- Expected TotalCutPercent: 15%

**Property B** (Should have good rent-to-price):
- CurrentPrice: $1,500,000
- EstimatedMonthlyRent: $5,500
- Expected RentToPriceRatio: 4.4%

**Property C** (Should have poor HOA score):
- CurrentPrice: $1,000,000
- MonthlyHOA: $1,500
- Expected HOAPercentOfPrice: 1.8% (Good)

### Validation Checklist
- [ ] All formulas return 0 when denominators are 0 (no div-by-zero errors)
- [ ] Percentages are properly scaled (multiply by 100)
- [ ] Currency values round to 2 decimals
- [ ] DistressFlag logic matches all conditions correctly
- [ ] PriceCutCount handles empty PriceHistory gracefully

---

## Advanced: Conditional Formatting

Set up these visual indicators in Airtable:

**DistressFlag**:
- High → Red background
- Medium → Yellow background
- Low → Green background

**BuyerFitScore**:
- 80-100 → Dark green
- 60-79 → Light green
- 40-59 → Yellow
- 0-39 → Red

**RentToPriceRatio**:
- ≥ 4.0% → Green (good investment)
- 3.0-3.9% → Yellow
- < 3.0% → Red (expensive)

**TotalCutPercent**:
- ≥ 10% → Red text, bold
- 5-9% → Orange text
- < 5% → Default

---

## Troubleshooting Common Formula Errors

### Error: #ERROR!
**Cause**: Field reference doesn't exist
**Fix**: Ensure field names match exactly (case-sensitive)

### Error: Division by zero
**Cause**: Missing `IF(denominator > 0, ...)` check
**Fix**: Wrap all divisions in conditional checks

### Incorrect Percentage Display
**Cause**: Forgetting to multiply by 100 or field type is wrong
**Fix**: Set field type to "Percent" and ensure formula multiplies by 100

### DistressFlag Always Shows "Low"
**Cause**: Field references incorrect or conditions too strict
**Fix**: Verify TotalCutPercent, PriceCutCount, DaysOnMarket all exist and have data
