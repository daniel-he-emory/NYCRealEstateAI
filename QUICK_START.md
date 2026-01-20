# 🚀 QUICK START - Get Your Demo Running in 3 Minutes

## Current Situation

Your database tables exist but have schema issues. The fastest fix is a quick manual reset.

---

## ⚡ 3-Minute Setup

### Step 1: Reset Database (1 min)

1. Open Supabase SQL Editor:
   **https://supabase.com/dashboard/project/uxjlxaengyhcgntgdjqn/editor**

2. Paste this SQL and click **RUN**:

```sql
-- Drop old tables
DROP TABLE IF EXISTS buyer_search_matched_properties CASCADE;
DROP TABLE IF EXISTS buyer_search_neighborhoods CASCADE;
DROP TABLE IF EXISTS buyer_searches CASCADE;
DROP TABLE IF EXISTS market_metrics CASCADE;
DROP TABLE IF EXISTS historical_sales CASCADE;
DROP TABLE IF EXISTS comparable_sales CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS neighborhoods CASCADE;
```

3. You'll see: "Success. No rows returned"

---

### Step 2: Create Fresh Tables (1 min)

1. **In the same SQL Editor**, paste the ENTIRE contents of:
   `/home/daniel/NYCRealEstateAI/migrations/001_initial_schema.sql`

   (Open the file, copy everything, paste into SQL Editor)

2. Click **RUN**

3. You'll see: "Success. No rows returned"

---

### Step 3: Load Sample Data (1 min)

```bash
# In your terminal:
source venv/bin/activate
python scripts/load_sample_data_supabase.py
```

Type `yes` when prompted.

You'll see:
```
✓ Generated 50 properties
✓ Inserted 50/50...
✅ Successfully loaded 50 properties!
```

---

### Step 4: Launch Demo (30 seconds)

```bash
streamlit run app.py
```

Browser opens automatically! 🎉

---

## Why Manual?

The access token you provided works for the PostgREST API but not the Management API needed for automated SQL execution. Manual SQL is actually faster and more reliable!

---

## What You Get

Your Streamlit demo will have:
- ✅ 50 realistic NYC properties
- ✅ Investment metrics (Cap Rate, GRM, etc.)
- ✅ Smart filters (price, beds, amenities)
- ✅ Distress flags (motivated sellers)
- ✅ Price history charts
- ✅ Market summaries

---

## Need Help?

If Step 3 fails, run:
```bash
python scripts/refresh_schema.py
python scripts/load_sample_data_supabase.py
```

---

## Files Created

I built these for you:
- `app.py` - Streamlit UI
- `scripts/load_sample_data_supabase.py` - Data generator
- `scripts/property_extractor_gemini.py` - AI scraper (Gemini Flash)
- `migrations/001_initial_schema.sql` - Database schema

**Total setup time: 3 minutes**
**Total cost: $0/month** (all free tiers!)
