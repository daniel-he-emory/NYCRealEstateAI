# Implementation Guide

Complete step-by-step guide to building the NYC Real Estate AI recommendation system.

## Prerequisites

- Airtable account (free tier works for testing)
- OpenAI API key (pay-as-you-go)
- Zapier or Make.com account (free tier)
- Retool or Glide account for UI (free tier)
- Basic familiarity with JSON and web forms

## Phase 1: Airtable Database Setup

### Step 1.1: Create Base

1. Log into Airtable at airtable.com
2. Click "Add a base" → "Start from scratch"
3. Name it "NYC Real Estate AI"

### Step 1.2: Create Tables

Create 5 tables with these exact names:
- Properties
- Neighborhoods
- HistoricalSales
- MarketMetrics
- BuyerSearches

### Step 1.3: Configure Properties Table

Follow the schema in `schemas/airtable-schema.json`. For each field:

**Basic Fields** (add these first):
1. PropertyID: Autonumber (automatically created as Record ID)
2. Address: Single line text
3. CurrentPrice: Currency (USD, no decimal precision for whole dollars)
4. OriginalPrice: Currency (USD)
5. PriceHistory: Long text
6. DaysOnMarket: Number (integer)
7. Bedrooms: Number (integer)
8. Bathrooms: Number (decimal, 1.0 precision)
9. SQFT: Number (integer)
10. MonthlyHOA: Currency (USD)
11. EstimatedMonthlyRent: Currency (USD)

**Checkbox Fields**:
12. HasElevator: Checkbox
13. HasDoorman: Checkbox
14. HasParking: Checkbox
15. HasGym: Checkbox
16. HasRoofDeck: Checkbox
17. PetFriendly: Checkbox

**Single Select Fields**:
18. Exposure: Single select → Add options: North, South, East, West, Corner, Multiple, Unknown
19. FloorLevel: Single select → Add options: Low (1-5), Mid (6-15), High (16-30), Penthouse (31+), Unknown
20. Status: Single select → Add options: Active, In Contract, Sold, Delisted, Price Change
21. DataSource: Single select → Add options: StreetEasy, Zillow, Realtor.com, Manual, API

**More Number Fields**:
22. FloorNumber: Number (integer)
23. SubwayDistance: Number (integer)
24. YearBuilt: Number (integer)
25. BuyerFitScore: Number (decimal, 1.0 precision)

**Date/Text Fields**:
26. LastSaleDate: Date
27. LastSalePrice: Currency (USD)
28. ACRISRecordID: Single line text
29. NearestSubwayLines: Single line text
30. ListingURL: URL
31. PropertyDescription: Long text

**Multiple Select Field**:
32. PropertyTags: Multiple select → Add options: Waterfront, Renovated, Prewar, New Construction, Loft, View, Outdoor Space, In-Unit Laundry, Storage

**Linked Record**:
33. Neighborhood: Link to another record → Select "Neighborhoods" table

**Formula Fields** (see FORMULAS.md for exact syntax):
34. PriceCutCount: Formula → `IF(PriceHistory, LEN(PriceHistory) - LEN(SUBSTITUTE(PriceHistory, '},{', '}')), 0)`
35. TotalCutPercent: Formula → `IF(AND(OriginalPrice > 0, CurrentPrice > 0), ROUND((OriginalPrice - CurrentPrice) / OriginalPrice * 100, 2), 0)` → Set field type to Percent
36. PricePerSQFT: Formula → `IF(SQFT > 0, ROUND(CurrentPrice / SQFT, 2), 0)` → Set to Currency
37. HOAPercentOfPrice: Formula → `IF(CurrentPrice > 0, ROUND((MonthlyHOA * 12) / CurrentPrice * 100, 2), 0)` → Set to Percent
38. AnnualRent: Formula → `EstimatedMonthlyRent * 12` → Set to Currency
39. RentToPriceRatio: Formula → `IF(CurrentPrice > 0, ROUND((EstimatedMonthlyRent * 12) / CurrentPrice * 100, 2), 0)` → Set to Percent
40. BuildingAge: Formula → `YEAR(TODAY()) - YearBuilt`
41. AppreciationSinceLastSale: Formula → `IF(AND(LastSalePrice > 0, CurrentPrice > 0), ROUND((CurrentPrice - LastSalePrice) / LastSalePrice * 100, 2), 0)` → Set to Percent
42. DistressFlag: Formula → `IF(AND(TotalCutPercent >= 10, PriceCutCount >= 2, DaysOnMarket >= 60), 'High', IF(OR(TotalCutPercent >= 5, PriceCutCount >= 1, DaysOnMarket >= 45), 'Medium', 'Low'))`

**Automatic Fields**:
43. DateAdded: Created time
44. LastUpdated: Last modified time

### Step 1.4: Configure Neighborhoods Table

1. NeighborhoodName: Single line text (primary field)
2. Borough: Single select → Manhattan, Brooklyn, Queens, Bronx, Staten Island
3. MedianPrice: Currency
4. MedianPricePerSQFT: Currency
5. MedianRent: Currency
6. AvgDaysOnMarket: Number (integer)
7. PriceChangeYoY: Percent
8. AvgSubwayAccess: Number (integer)
9. WalkScore: Number (integer, 0-100)
10. TransitScore: Number (integer, 0-100)
11. NeighborhoodNotes: Long text
12. RentToPriceRatio: Formula → `IF(MedianPrice > 0, ROUND((MedianRent * 12) / MedianPrice * 100, 2), 0)` → Percent
13. TotalListings: Count (Rollup from Properties → Neighborhood link)

### Step 1.5: Configure HistoricalSales Table

1. DocumentID: Single line text (primary)
2. RecordedDate: Date
3. Address: Single line text
4. Borough: Single select (same options as Neighborhoods)
5. Neighborhood: Link to Neighborhoods table
6. SalePrice: Currency
7. PropertyType: Single select → Condo, Co-op, Townhouse, Multi-family, Other
8. Bedrooms: Number (integer)
9. SQFT: Number (integer)
10. PricePerSQFT: Formula → `IF(SQFT > 0, ROUND(SalePrice / SQFT, 2), 0)` → Currency

### Step 1.6: Configure MarketMetrics Table

1. MetricID: Autonumber
2. Date: Date
3. Neighborhood: Link to Neighborhoods (allow blank for citywide data)
4. AvgPricePerSQFT: Currency
5. MedianSalePrice: Currency
6. SalesVolume: Number (integer)
7. AvgDaysOnMarket: Number (integer)
8. InventoryCount: Number (integer)

### Step 1.7: Configure BuyerSearches Table

1. SearchID: Autonumber
2. SearchDate: Created time
3. RawInput: Long text
4. ParsedCriteria: Long text (will store JSON from OpenAI)
5. BedsMin: Number (integer)
6. BedsMax: Number (integer)
7. BathsMin: Number (decimal)
8. PriceMin: Currency
9. PriceMax: Currency
10. RequiredAmenities: Multiple select → Elevator, Doorman, Parking, Gym, Roof Deck, Pet Friendly, In-Unit Laundry
11. PreferredNeighborhoods: Link to Neighborhoods (allow linking to multiple)
12. MaxSubwayDistance: Number (integer)
13. MaxHOAMonthly: Currency
14. MatchedProperties: Link to Properties (allow multiple)
15. ResultsCount: Count (Rollup from MatchedProperties)

### Step 1.8: Import Sample Data

1. Download sample data from `examples/sample-neighborhoods.json`
2. In Neighborhoods table → Click "..." menu → Import data → JSON
3. Map fields accordingly
4. Download `examples/sample-properties.json`
5. In Properties table → Import similarly
6. **Important**: After importing properties, manually link each to its Neighborhood using the neighborhood name

### Step 1.9: Create Views

**Properties Table Views:**

1. **All Active Listings**:
   - Filter: Status = "Active"
   - Sort: BuyerFitScore (descending)
   - Hide: PriceHistory, PropertyDescription, ACRISRecordID, DateAdded

2. **High Distress Signals**:
   - Filter: DistressFlag = "High"
   - Sort: TotalCutPercent (descending)
   - Color code: Red background for high distress

3. **Best Value (Rent-to-Price)**:
   - Filter: RentToPriceRatio ≥ 4
   - Sort: RentToPriceRatio (descending)

4. **Recent Price Cuts**:
   - Filter: Status = "Price Change"
   - Sort: LastUpdated (descending)

### Step 1.10: Set Up Conditional Formatting

**DistressFlag Field**:
- When "High" → Red background
- When "Medium" → Yellow background
- When "Low" → Green background

**BuyerFitScore Field**:
- ≥ 80 → Dark green text
- 60-79 → Light green text
- 40-59 → Orange text
- < 40 → Red text

**TotalCutPercent Field**:
- ≥ 10% → Red bold text
- 5-9% → Orange text

---

## Phase 2: Natural Language Parser (OpenAI + Zapier)

### Step 2.1: Create Input Form

**Option A: Google Forms (Easiest)**
1. Create form at forms.google.com
2. Add question: "Describe your ideal NYC property" (Paragraph response)
3. Add email collection for follow-up
4. Save form and note the form ID

**Option B: Typeform (More polished)**
1. Create account at typeform.com
2. Create form with long text question
3. Enable webhooks in integrations

### Step 2.2: Set Up Zapier Workflow

1. **Trigger**: Google Forms → New Response
   - Connect your Google account
   - Select the form you created

2. **Action 1**: OpenAI → Conversation (or Text Completion)
   - Connect OpenAI account with API key
   - Model: gpt-4 or gpt-3.5-turbo
   - System Message:
   ```
   You are a real estate search parser. Extract structured criteria from natural language property descriptions.

   Return ONLY valid JSON with these fields:
   {
     "beds_min": number or null,
     "beds_max": number or null,
     "baths_min": number or null,
     "price_min": number or null,
     "price_max": number or null,
     "amenities": array of strings,
     "exposure_preference": string or null,
     "floor_preference": string or null,
     "hoa_max_monthly": number or null,
     "subway_max_minutes": number or null,
     "neighborhoods": array of strings or null,
     "must_have": array of strings,
     "nice_to_have": array of strings
   }

   Example: "2 bed under $1.8M, elevator, south facing, near subway in LIC"
   Output: {"beds_min":2,"price_max":1800000,"amenities":["elevator"],"exposure_preference":"south","subway_max_minutes":10,"neighborhoods":["Long Island City"]}
   ```
   - User Message: `Parse this property search: {form response text}`

3. **Action 2**: Code by Zapier (JavaScript)
   - Parse the JSON response from OpenAI
   - Clean and validate the data
   ```javascript
   const parsed = JSON.parse(inputData.openai_response);

   // Map amenities to Airtable field format
   const amenityMap = {
     'elevator': 'Elevator',
     'doorman': 'Doorman',
     'parking': 'Parking',
     'gym': 'Gym',
     'roof deck': 'Roof Deck',
     'pet friendly': 'Pet Friendly'
   };

   const mappedAmenities = (parsed.amenities || []).map(a =>
     amenityMap[a.toLowerCase()] || a
   );

   return {
     beds_min: parsed.beds_min,
     beds_max: parsed.beds_max,
     price_max: parsed.price_max,
     required_amenities: mappedAmenities,
     max_subway: parsed.subway_max_minutes,
     neighborhoods: parsed.neighborhoods,
     raw_json: JSON.stringify(parsed)
   };
   ```

4. **Action 3**: Airtable → Create Record
   - Select your base: "NYC Real Estate AI"
   - Select table: "BuyerSearches"
   - Map fields:
     - RawInput: {original form response}
     - ParsedCriteria: {raw_json from code step}
     - BedsMin: {beds_min}
     - BedsMax: {beds_max}
     - PriceMax: {price_max}
     - RequiredAmenities: {required_amenities}
     - MaxSubwayDistance: {max_subway}

5. **Action 4**: Airtable → Find Records
   - Table: Properties
   - Build filters dynamically:
     - Bedrooms ≥ {beds_min}
     - CurrentPrice ≤ {price_max}
     - Status = "Active"
   - Max records: 50

6. **Action 5**: Airtable → Update Record
   - Table: BuyerSearches
   - Record ID: {from step 3}
   - Field: MatchedProperties → {record IDs from step 4}

7. Test the Zap with sample inputs

### Step 2.3: Test Cases for NLP Parser

Run these through your form to verify parsing:

1. **Simple search**: "2 bedroom under $1.5M"
   - Expected: `{"beds_min":2,"price_max":1500000}`

2. **Complex search**: "Looking for 2-3 bed condo under $1.8M with elevator and doorman, lots of natural light, near subway in LIC or Manhattan, low HOA"
   - Expected: `{"beds_min":2,"beds_max":3,"price_max":1800000,"amenities":["elevator","doorman"],"exposure_preference":"good light","subway_max_minutes":10,"neighborhoods":["Long Island City","Manhattan"],"hoa_preference":"low"}`

3. **Investment focus**: "1 bed around $900K, high rent-to-price ratio, near subway"
   - Expected: `{"beds_min":1,"price_max":950000,"price_min":850000,"subway_max_minutes":10,"must_have":["high rental yield"]}`

---

## Phase 3: Ranking Engine Implementation

### Step 3.1: Create BuyerFitScore Calculation Script

Since Airtable formulas can't reference user preferences dynamically, implement scoring as an Airtable Automation:

1. In Airtable → Automations → Create automation
2. Trigger: "When record matches conditions"
   - Table: BuyerSearches
   - Condition: When ParsedCriteria is not empty

3. Action: "Run script"
```javascript
// Get the search record that triggered
let searchTable = base.getTable("BuyerSearches");
let searchRecord = await searchTable.selectRecordAsync(input.config().searchRecordId);

// Parse criteria
let criteria = JSON.parse(searchRecord.getCellValue("ParsedCriteria"));
let userMaxPrice = criteria.price_max || 5000000;
let requiredAmenities = criteria.amenities || [];

// Get all active properties
let propertiesTable = base.getTable("Properties");
let propertiesQuery = await propertiesTable.selectRecordsAsync({
  fields: ["Address", "CurrentPrice", "HOAPercentOfPrice", "SubwayDistance",
           "HasElevator", "HasDoorman", "DistressFlag", "Exposure", "Status"]
});

let scoredProperties = [];

for (let property of propertiesQuery.records) {
  if (property.getCellValue("Status") !== "Active") continue;

  let score = 0;
  let currentPrice = property.getCellValue("CurrentPrice") || 0;

  // Price Match (40 points)
  if (currentPrice <= userMaxPrice) {
    let utilizationRatio = currentPrice / userMaxPrice;
    score += utilizationRatio <= 0.85 ? 40 : 40 * (1 - utilizationRatio);
  }

  // HOA Impact (20 points)
  let hoaPercent = property.getCellValue("HOAPercentOfPrice") || 0;
  if (hoaPercent <= 1.5) score += 20;
  else if (hoaPercent <= 2.5) score += 15;
  else if (hoaPercent <= 3.5) score += 10;
  else score += 5;

  // Commute (15 points)
  let subwayDist = property.getCellValue("SubwayDistance") || 99;
  if (subwayDist <= 5) score += 15;
  else if (subwayDist <= 10) score += 10;
  else if (subwayDist <= 15) score += 5;

  // Amenities (15 points)
  let amenityScore = 0;
  if (requiredAmenities.includes("elevator") && property.getCellValue("HasElevator")) {
    amenityScore += 7.5;
  }
  if (requiredAmenities.includes("doorman") && property.getCellValue("HasDoorman")) {
    amenityScore += 7.5;
  }
  score += Math.min(amenityScore, 15);

  // Distress Bonus (10 points)
  let distress = property.getCellValue("DistressFlag");
  if (distress === "High") score += 10;
  else if (distress === "Medium") score += 5;

  // Exposure Bonus (5 points)
  let exposure = property.getCellValue("Exposure");
  if (["South", "Corner", "Multiple"].includes(exposure)) score += 5;

  // Update property with score
  await propertiesTable.updateRecordAsync(property.id, {
    "BuyerFitScore": Math.round(score)
  });

  scoredProperties.push({
    id: property.id,
    score: Math.round(score)
  });
}

console.log(`Scored ${scoredProperties.length} properties`);
```

### Step 3.2: Alternative - Zapier Implementation

If you prefer Zapier over Airtable Automation:

1. Add to existing Zap after finding records
2. Add "Looping by Zapier" action to iterate through matched properties
3. For each property, run Code by Zapier with scoring logic
4. Update property record with calculated score

---

## Phase 4: Dashboard & UI

### Option A: Retool (Recommended for flexibility)

#### Step 4.1: Connect Data Source
1. Create Retool account
2. Add Resource → Airtable
3. Enter API key and base ID

#### Step 4.2: Build Screen 1 - Search Interface

**Components:**
1. Text Area Input
   - Label: "Describe your dream home..."
   - Placeholder: "Example: 2 bed under $1.8M, elevator, south-facing, near 7 train in LIC or Manhattan"
   - ID: `searchInput`

2. Button: "Find Properties"
   - onClick: Trigger query `submitSearch`

**Queries:**
- `submitSearch`:
  - Resource: Airtable
  - Action: Create record
  - Table: BuyerSearches
  - Fields: RawInput = {{searchInput.value}}
  - Success trigger: Navigate to Results screen

#### Step 4.3: Build Screen 2 - Results List

**Queries:**
- `getTopMatches`:
  - Resource: Airtable
  - Action: List records
  - Table: Properties
  - Filter: Status = "Active" AND BuyerFitScore > 0
  - Sort: BuyerFitScore DESC
  - Max records: 10

**Components:**
1. List View (data source: `{{getTopMatches.data}}`)
   - Card for each property:
     - Image: Property photo (if available)
     - Text: `{{item.Address}}`
     - Text: `${{item.CurrentPrice.toLocaleString()}}`
     - Badge: Fit Score `{{item.BuyerFitScore}}` (color: green if >80, yellow if 60-79, red if <60)
     - Badge: Distress level (if High or Medium)
     - Icons: Show elevator/doorman icons if true
     - Button: "View Details" → Navigate to detail screen with `{{item.id}}`

#### Step 4.4: Build Screen 3 - Property Detail

**Queries:**
- `getPropertyDetail`:
  - Resource: Airtable
  - Action: Get record
  - Table: Properties
  - Record ID: `{{urlparams.propertyId}}`

- `getNeighborhoodData`:
  - Resource: Airtable
  - Action: Get record
  - Table: Neighborhoods
  - Record ID: `{{getPropertyDetail.data.Neighborhood[0]}}`

**Layout:**
- **Header**: Address, Price, Fit Score badge
- **Key Details Card**:
  - Beds, Baths, SQFT
  - Floor level, Exposure
  - Year built, Building age
  - Amenities icons
- **Valuation Context Card**:
  - Rent-to-Price: `{{getPropertyDetail.data.RentToPriceRatio}}%`
    - Compare to neighborhood avg: `{{getNeighborhoodData.data.RentToPriceRatio}}%`
    - Show ✓ or ✗ indicator
  - Price/SQFT: `${{getPropertyDetail.data.PricePerSQFT}}`
    - Compare to neighborhood median
  - HOA %: `{{getPropertyDetail.data.HOAPercentOfPrice}}%`
    - Grade: Excellent/Good/Fair/Poor
- **Seller Signals Card**:
  - Original price → Current price
  - Price cuts: `{{getPropertyDetail.data.PriceCutCount}}`
  - Total cut: `{{getPropertyDetail.data.TotalCutPercent}}%`
  - Days on market: `{{getPropertyDetail.data.DaysOnMarket}}`
  - Distress level with explanation
- **Description**: Full property description
- **Listing Link**: Button to open ListingURL

#### Step 4.5: Build Screen 4 - Add Property

**Components:**
1. Text Input: "Listing URL"
2. Button: "Auto-Extract" (Phase 5 feature)
3. Manual entry form (all property fields)
4. Button: "Save Property"

**Query:**
- `createProperty`:
  - Action: Create record in Properties table
  - Map all form fields

### Option B: Glide (Easier, less customizable)

1. Create new Glide app
2. Connect to Airtable base
3. Use built-in components:
   - Cards for property list
   - Detail screen auto-generated from table
   - Forms for search and add property
4. Customize styling and branding

---

## Phase 5: Data Extraction

### Option A: Manual Python Script

See `scripts/property_extractor.py` (to be created) for scraping logic.

### Option B: Phantombuster

1. Create Phantombuster account
2. Use "StreetEasy Profile Scraper" phantom
3. Configure with property URLs
4. Export to CSV
5. Import to Airtable

---

## Testing & Validation

### Test Checklist

- [ ] All Airtable formulas calculate correctly
- [ ] Sample properties show expected DistressFlag values
- [ ] NLP parser extracts criteria from various inputs
- [ ] BuyerFitScore ranks properties logically
- [ ] Dashboard displays data accurately
- [ ] Valuation context comparisons are correct
- [ ] Search → Results → Detail flow works smoothly

### Sample Queries to Test

1. "2 bed $1.5M elevator LIC" → Should return LIC properties, sorted by fit
2. "High ROI investment property under $1M" → Should prioritize high rent-to-price ratio
3. "3 bed Manhattan doorman south facing" → Should filter correctly and bonus for exposure

---

## Maintenance & Updates

### Weekly Tasks
- Update active listings statuses
- Add new properties from StreetEasy
- Archive sold properties

### Monthly Tasks
- Update neighborhood median prices
- Refresh MarketMetrics table with latest data
- Review and adjust BuyerFitScore weights based on feedback

---

## Cost Estimate

- **Airtable Free**: 1,200 records (sufficient for MVP)
- **OpenAI API**: ~$0.002 per search (100 searches = $0.20)
- **Zapier Free**: 100 tasks/month (100 searches)
- **Retool Free**: Unlimited apps, 5 users
- **Total**: ~$5-15/month for moderate usage

---

## Next Steps

1. Complete Phase 1 (Airtable setup) - takes ~2 hours
2. Set up Phase 2 (NLP parser) - takes ~1 hour
3. Implement Phase 3 (scoring) - takes ~1 hour
4. Build Phase 4 (UI) - takes ~3-4 hours
5. Test with real data - ongoing

**Total MVP build time: ~8-10 hours**

For questions or issues, document in project issues or README.
