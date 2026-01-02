# OpenAI Natural Language Parser

Complete guide to the natural language search parser that converts buyer descriptions into structured search criteria.

## System Prompt

Use this exact prompt for the OpenAI API call:

```
You are a real estate search criteria extractor for NYC properties. Your job is to parse natural language property descriptions into structured JSON.

Extract the following fields from user input:

REQUIRED STRUCTURE:
{
  "beds_min": number or null,
  "beds_max": number or null,
  "baths_min": number or null,
  "baths_max": number or null,
  "price_min": number or null,
  "price_max": number or null,
  "amenities": array of strings or [],
  "exposure_preference": string or null,
  "floor_preference": string or null,
  "hoa_preference": string or null,
  "hoa_max_monthly": number or null,
  "subway_max_minutes": number or null,
  "neighborhoods": array of strings or [],
  "must_have": array of critical requirements or [],
  "nice_to_have": array of preferences or [],
  "special_criteria": string or null
}

PARSING RULES:

1. BEDROOMS:
   - "2 bed" or "2 bedroom" → beds_min: 2, beds_max: null
   - "2-3 bed" → beds_min: 2, beds_max: 3
   - "at least 2 bed" → beds_min: 2, beds_max: null
   - "1 or 2 bed" → beds_min: 1, beds_max: 2

2. BATHROOMS:
   - Same logic as bedrooms
   - Accept decimals: "1.5 bath" → baths_min: 1.5

3. PRICE:
   - "under $1.8M" → price_max: 1800000
   - "$1.5-1.8M" → price_min: 1500000, price_max: 1800000
   - "around $1.5M" → price_min: 1400000, price_max: 1600000 (±$100k)
   - Accept formats: $1.8M, $1,800,000, 1.8 million

4. AMENITIES (standardize to these exact terms):
   - "elevator" → "elevator"
   - "doorman" or "concierge" → "doorman"
   - "parking" or "garage" → "parking"
   - "gym" or "fitness" or "fitness center" → "gym"
   - "roof deck" or "rooftop" → "roof deck"
   - "pet friendly" or "pets allowed" → "pet friendly"
   - "laundry" or "washer/dryer" → "in-unit laundry"

5. LOCATION:
   - Common abbreviations:
     * "LIC" → "Long Island City"
     * "UWS" → "Upper West Side"
     * "UES" → "Upper East Side"
     * "FiDi" → "Financial District"
     * "DUMBO" → "DUMBO"
   - "Manhattan" alone → ["Manhattan"] (borough-level)
   - Multiple: "LIC or Manhattan" → ["Long Island City", "Manhattan"]

6. LIGHT/EXPOSURE:
   - "lots of light", "sunny", "bright" → exposure_preference: "good light"
   - "south facing", "southern exposure" → exposure_preference: "south"
   - "corner unit" → exposure_preference: "corner"

7. FLOOR PREFERENCE:
   - "high floor" → floor_preference: "high"
   - "penthouse" → floor_preference: "penthouse"
   - "low floor" → floor_preference: "low"

8. HOA/MAINTENANCE:
   - "low HOA" → hoa_preference: "low"
   - "HOA under $1000/month" → hoa_max_monthly: 1000

9. COMMUTE:
   - "near subway", "close to transit" → subway_max_minutes: 10
   - "walking distance to subway" → subway_max_minutes: 10
   - "5 min walk to subway" → subway_max_minutes: 5

10. INVESTMENT CRITERIA:
    - "high ROI", "good rental yield", "investment property" → Add to special_criteria

EXAMPLES:

Input: "2 bed under $1.8M, elevator, lots of light, near subway, low HOA"
Output:
{
  "beds_min": 2,
  "beds_max": null,
  "baths_min": null,
  "baths_max": null,
  "price_min": null,
  "price_max": 1800000,
  "amenities": ["elevator"],
  "exposure_preference": "good light",
  "floor_preference": null,
  "hoa_preference": "low",
  "hoa_max_monthly": null,
  "subway_max_minutes": 10,
  "neighborhoods": [],
  "must_have": ["elevator", "low HOA"],
  "nice_to_have": ["good light", "near subway"],
  "special_criteria": null
}

Input: "Looking for 2-3 bedroom condo in LIC or Manhattan, $1.5-1.8M range, doorman building, south facing preferred, pet friendly"
Output:
{
  "beds_min": 2,
  "beds_max": 3,
  "baths_min": null,
  "baths_max": null,
  "price_min": 1500000,
  "price_max": 1800000,
  "amenities": ["doorman", "pet friendly"],
  "exposure_preference": "south",
  "floor_preference": null,
  "hoa_preference": null,
  "hoa_max_monthly": null,
  "subway_max_minutes": null,
  "neighborhoods": ["Long Island City", "Manhattan"],
  "must_have": ["doorman", "pet friendly"],
  "nice_to_have": ["south facing"],
  "special_criteria": null
}

Input: "1 bed investment property under $1M, high rental yield, close to subway"
Output:
{
  "beds_min": 1,
  "beds_max": null,
  "baths_min": null,
  "baths_max": null,
  "price_min": null,
  "price_max": 1000000,
  "amenities": [],
  "exposure_preference": null,
  "floor_preference": null,
  "hoa_preference": null,
  "hoa_max_monthly": null,
  "subway_max_minutes": 10,
  "neighborhoods": [],
  "must_have": [],
  "nice_to_have": [],
  "special_criteria": "investment property with high rental yield"
}

IMPORTANT:
- Return ONLY valid JSON, no additional text
- All price values must be in dollars (not millions)
- Use null for missing values, not undefined or empty string
- Standardize amenity names exactly as shown above
- Expand neighborhood abbreviations to full names

Now parse this user query into JSON:
```

---

## API Implementation

### Using OpenAI Python SDK

```python
import openai
import json

openai.api_key = "your-api-key-here"

def parse_search_query(user_input: str) -> dict:
    """
    Parse natural language property search into structured criteria.

    Args:
        user_input: User's natural language description

    Returns:
        Dictionary with structured search criteria
    """

    system_prompt = """[Insert full system prompt from above]"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Now parse this user query into JSON:\n\n{user_input}"}
            ],
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=500
        )

        # Extract JSON from response
        parsed_json = json.loads(response.choices[0].message.content)

        return {
            "success": True,
            "criteria": parsed_json,
            "raw_input": user_input
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "Failed to parse JSON from OpenAI response",
            "raw_response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Example usage
if __name__ == "__main__":
    test_queries = [
        "2 bed under $1.8M, elevator, lots of light, near subway in LIC",
        "3 bedroom Manhattan doorman building $2-2.5M south facing pet friendly",
        "Investment property 1-2 bed under $1.2M high ROI Brooklyn or Queens"
    ]

    for query in test_queries:
        result = parse_search_query(query)
        if result["success"]:
            print(f"\nQuery: {query}")
            print(f"Parsed: {json.dumps(result['criteria'], indent=2)}")
        else:
            print(f"\nERROR parsing '{query}': {result['error']}")
```

### Using OpenAI Node.js SDK

```javascript
const { Configuration, OpenAIApi } = require("openai");

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

async function parseSearchQuery(userInput) {
  const systemPrompt = `[Insert full system prompt from above]`;

  try {
    const response = await openai.createChatCompletion({
      model: "gpt-4",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: `Now parse this user query into JSON:\n\n${userInput}` }
      ],
      temperature: 0.1,
      max_tokens: 500,
    });

    const parsedCriteria = JSON.parse(response.data.choices[0].message.content);

    return {
      success: true,
      criteria: parsedCriteria,
      raw_input: userInput,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

// Example usage
const testQuery = "2 bed under $1.8M, elevator, lots of light, near subway in LIC";
parseSearchQuery(testQuery).then(result => {
  console.log(JSON.stringify(result, null, 2));
});
```

---

## Test Cases

### Test Case 1: Simple Budget + Beds
**Input**: `"2 bedroom under $1.5M"`

**Expected Output**:
```json
{
  "beds_min": 2,
  "beds_max": null,
  "price_max": 1500000,
  "amenities": [],
  "neighborhoods": [],
  "must_have": [],
  "nice_to_have": []
}
```

### Test Case 2: Range with Amenities
**Input**: `"2-3 bed $1.5-1.8M elevator doorman parking LIC or Manhattan"`

**Expected Output**:
```json
{
  "beds_min": 2,
  "beds_max": 3,
  "price_min": 1500000,
  "price_max": 1800000,
  "amenities": ["elevator", "doorman", "parking"],
  "neighborhoods": ["Long Island City", "Manhattan"],
  "must_have": ["elevator", "doorman", "parking"],
  "nice_to_have": []
}
```

### Test Case 3: Light/Exposure Preference
**Input**: `"2 bed south facing lots of natural light corner unit"`

**Expected Output**:
```json
{
  "beds_min": 2,
  "exposure_preference": "south",
  "must_have": ["south facing", "corner unit"],
  "nice_to_have": ["lots of light"]
}
```

### Test Case 4: Investment Focus
**Input**: `"1 bed under $900K high rental yield good ROI near subway"`

**Expected Output**:
```json
{
  "beds_min": 1,
  "price_max": 900000,
  "subway_max_minutes": 10,
  "special_criteria": "investment property with high rental yield",
  "must_have": [],
  "nice_to_have": ["high ROI", "near subway"]
}
```

### Test Case 5: Complex Query
**Input**: `"Looking for a 2-3 bedroom condo in Hell's Kitchen or UWS, budget $1.8-2.2M, need elevator and doorman, prefer south facing with good light, pet friendly, low monthly HOA (under $1200), walking distance to subway"`

**Expected Output**:
```json
{
  "beds_min": 2,
  "beds_max": 3,
  "price_min": 1800000,
  "price_max": 2200000,
  "amenities": ["elevator", "doorman", "pet friendly"],
  "exposure_preference": "south",
  "hoa_max_monthly": 1200,
  "subway_max_minutes": 10,
  "neighborhoods": ["Hell's Kitchen", "Upper West Side"],
  "must_have": ["elevator", "doorman", "pet friendly", "low HOA"],
  "nice_to_have": ["south facing", "good light", "near subway"]
}
```

### Test Case 6: Abbreviations
**Input**: `"2BR FiDi or DUMBO $1.2-1.5M gym roof deck"`

**Expected Output**:
```json
{
  "beds_min": 2,
  "price_min": 1200000,
  "price_max": 1500000,
  "amenities": ["gym", "roof deck"],
  "neighborhoods": ["Financial District", "DUMBO"],
  "must_have": ["gym", "roof deck"]
}
```

---

## Validation & Error Handling

### Post-Processing Validation

After receiving JSON from OpenAI, validate and clean:

```python
def validate_and_clean_criteria(criteria: dict) -> dict:
    """Validate and clean parsed criteria."""

    # Ensure price_max >= price_min
    if criteria.get("price_min") and criteria.get("price_max"):
        if criteria["price_min"] > criteria["price_max"]:
            criteria["price_min"], criteria["price_max"] = \
                criteria["price_max"], criteria["price_min"]

    # Ensure beds_max >= beds_min
    if criteria.get("beds_min") and criteria.get("beds_max"):
        if criteria["beds_min"] > criteria["beds_max"]:
            criteria["beds_min"], criteria["beds_max"] = \
                criteria["beds_max"], criteria["beds_min"]

    # Standardize amenities to match Airtable field values
    amenity_map = {
        "elevator": "Elevator",
        "doorman": "Doorman",
        "parking": "Parking",
        "gym": "Gym",
        "roof deck": "Roof Deck",
        "pet friendly": "Pet Friendly",
        "in-unit laundry": "In-Unit Laundry"
    }

    if criteria.get("amenities"):
        criteria["amenities"] = [
            amenity_map.get(a.lower(), a)
            for a in criteria["amenities"]
        ]

    # Cap subway distance at reasonable max
    if criteria.get("subway_max_minutes"):
        criteria["subway_max_minutes"] = min(criteria["subway_max_minutes"], 20)

    return criteria
```

### Handling Ambiguous Queries

For queries that are too vague, return a validation error:

```python
def is_query_too_vague(criteria: dict) -> bool:
    """Check if query provides minimum searchable criteria."""

    has_beds = criteria.get("beds_min") is not None
    has_price = criteria.get("price_max") is not None or \
                criteria.get("price_min") is not None
    has_location = len(criteria.get("neighborhoods", [])) > 0

    # Need at least ONE of: beds, price, or location
    return not (has_beds or has_price or has_location)


# Usage
criteria = parse_search_query(user_input)["criteria"]
if is_query_too_vague(criteria):
    return {
        "error": "Please provide at least one of: number of bedrooms, price range, or neighborhood preference"
    }
```

---

## Cost Optimization

### Model Selection

| Model | Cost per 1K tokens | Speed | Accuracy |
|-------|-------------------|-------|----------|
| gpt-4 | $0.03 input / $0.06 output | Slower | Highest |
| gpt-3.5-turbo | $0.001 input / $0.002 output | Fast | Good |

**Recommendation**: Use gpt-3.5-turbo for production (30x cheaper), reserve gpt-4 for complex/ambiguous queries.

### Estimated Costs

- Average query uses ~800 tokens (600 system prompt + 200 response)
- **gpt-3.5-turbo**: ~$0.002 per search
- **gpt-4**: ~$0.05 per search

**100 searches/month**:
- gpt-3.5-turbo: $0.20/month
- gpt-4: $5.00/month

---

## Integration with Airtable

### Storing Parsed Criteria

```python
from pyairtable import Table

def save_search_to_airtable(raw_input: str, criteria: dict):
    """Save search query and parsed criteria to Airtable."""

    table = Table('your_api_key', 'your_base_id', 'BuyerSearches')

    record = {
        "RawInput": raw_input,
        "ParsedCriteria": json.dumps(criteria),
        "BedsMin": criteria.get("beds_min"),
        "BedsMax": criteria.get("beds_max"),
        "PriceMin": criteria.get("price_min"),
        "PriceMax": criteria.get("price_max"),
        "RequiredAmenities": criteria.get("amenities", []),
        "MaxSubwayDistance": criteria.get("subway_max_minutes")
    }

    # Remove None values
    record = {k: v for k, v in record.items() if v is not None}

    created_record = table.create(record)
    return created_record['id']
```

---

## Debugging Tips

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Log OpenAI requests/responses
response = openai.ChatCompletion.create(...)
logging.debug(f"OpenAI Response: {response.choices[0].message.content}")
```

### Common Issues

**Issue**: OpenAI returns text instead of JSON
- **Fix**: Emphasize "Return ONLY valid JSON" in system prompt
- **Fix**: Add `response_format={"type": "json_object"}` (GPT-4 Turbo+)

**Issue**: Inconsistent amenity names
- **Fix**: Use post-processing validation to map variants

**Issue**: Prices interpreted incorrectly
- **Fix**: Provide more examples of price formats in system prompt

---

## Advanced: Few-Shot Learning

For better accuracy, add more examples to the system prompt:

```
ADDITIONAL EXAMPLES:

Input: "Spacious 3BR with outdoor space, pet-friendly building in Park Slope, up to $2M"
Output: {"beds_min":3,"price_max":2000000,"amenities":["pet friendly"],"neighborhoods":["Park Slope"],"must_have":["outdoor space","pet friendly"]}

Input: "Loft-style 1-2 bed with high ceilings, Brooklyn, $900-1.2M, elevator a must"
Output: {"beds_min":1,"beds_max":2,"price_min":900000,"price_max":1200000,"amenities":["elevator"],"neighborhoods":["Brooklyn"],"must_have":["elevator"],"nice_to_have":["loft-style","high ceilings"]}
```

---

## Next Steps

1. Test system prompt with 20+ real user queries
2. Refine prompt based on parsing errors
3. Implement validation logic
4. Integrate with Zapier or backend API
5. Monitor parsing accuracy and collect edge cases

For implementation in Zapier, see `IMPLEMENTATION.md` Phase 2.
