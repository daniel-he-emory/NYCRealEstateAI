# 🚀 NYC Real Estate AI - Demo Quick Start Guide

## What We Built

A fully functional NYC real estate search engine with:
- ✅ **Supabase PostgreSQL database** (scalable, free tier)
- ✅ **Google Gemini Flash AI** (cheaper than OpenAI, faster)
- ✅ **Sample data generator** (50+ realistic properties)
- ✅ **Property web scraper** (extracts data from listing URLs)
- ✅ **Streamlit UI** (beautiful, interactive web interface)
- ✅ **Investment metrics** (Cap Rate, GRM, Cash-on-Cash, etc.)

---

## 🎯 Get Your Demo Running (5 minutes)

### Step 1: Set Up Database (2 minutes)

1. **Open Supabase SQL Editor:**
   - Go to: https://supabase.com/dashboard/project/uxjlxaengyhcgntgdjqn/editor

2. **Run the migration:**
   - Open the file: `migrations/001_initial_schema.sql`
   - Copy ALL the SQL content
   - Paste into Supabase SQL Editor
   - Click **"RUN"** button (or press Ctrl+Enter)

3. **Wait 5-10 seconds** - it will create 6 tables with all the columns!

---

### Step 2: Load Sample Data (2 minutes)

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Load 50 sample properties
python scripts/load_sample_data_supabase.py
```

When prompted, type **yes** and press Enter.

You'll see:
```
✓ Generated 50 properties
✓ Inserting into Supabase...
✓ Inserted 50/50...
✅ SAMPLE DATA LOADED!
```

---

### Step 3: Launch the Demo (1 minute)

```bash
streamlit run app.py
```

Your browser will open automatically to http://localhost:8501

**That's it! 🎉**

---

## 🎨 Demo Features

### Search & Filter
- **Neighborhoods**: Filter by Long Island City, Hell's Kitchen, DUMBO, etc.
- **Price Range**: Min/Max sliders
- **Bedrooms**: 1-5+ BR options
- **Amenities**: Elevator, Doorman, Gym, Parking, Pet-friendly

### Property Cards Show:
- 📍 Address & Neighborhood
- 💰 Price, $/SQFT, HOA fees
- 📊 Days on market, Status
- 🔥 Distress flags (motivated sellers)
- 📈 Investment metrics (Cap Rate, GRM, Rent ratio)
- 🏢 Amenities icons
- 📉 Price history charts
- 🗺️ Subway access

### Investment Analysis
Toggle "Show Investment Metrics" to see:
- **Cap Rate** - Net Operating Income / Price (aim for 3-5%)
- **GRM** - Gross Rent Multiplier (lower is better, ideal <15x)
- **Rent/Price Ratio** - Annual rent as % of price
- Color-coded ratings (Green = Good, Orange = Fair, Red = Poor)

### Market Summary
Bottom stats show:
- Average price & price/sqft
- Average days on market
- Average cap rate across all results

---

## 🤖 Scrape Real Listings (Bonus)

Want to add REAL properties from the web?

```bash
python scripts/property_extractor_gemini.py https://streeteasy.com/building/...
```

The AI will:
1. Fetch the listing page
2. Extract all property details using Gemini Flash
3. Auto-detect neighborhood
4. Save to Supabase

**Bulk import:**
```bash
# Create a file with URLs (one per line)
python scripts/property_extractor_gemini.py --bulk urls.txt
```

---

## 📂 File Structure

```
NYCRealEstateAI/
├── app.py                              # 🎨 Streamlit UI (DEMO INTERFACE)
├── migrations/
│   └── 001_initial_schema.sql          # Database schema (run this in Supabase)
├── scripts/
│   ├── setup_database.py               # Test Supabase connection
│   ├── load_sample_data_supabase.py    # 🏗️ Generate & load 50 properties
│   └── property_extractor_gemini.py    # 🤖 Scrape properties with Gemini AI
├── .env                                # Your API keys
└── requirements.txt                    # Python dependencies
```

---

## 🔧 Troubleshooting

### "Module not found" errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Could not find the table" error
You need to run the SQL migration first (see Step 1 above)

### Streamlit won't start
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
which streamlit  # Should show: /home/daniel/NYCRealEstateAI/venv/bin/streamlit
```

### No data showing in UI
1. Check if tables exist: https://supabase.com/dashboard/project/uxjlxaengyhcgntgdjqn/editor
2. Run the data loader again: `python scripts/load_sample_data_supabase.py`

---

## 🎬 Demo Tips

### For Investors
1. Enable "Show Investment Metrics"
2. Sort by "Cap Rate (Highest)"
3. Filter for 2-3BR (easiest to rent)
4. Look for High Distress flags (negotiation opportunity)

### For First-Time Buyers
1. Set your price range
2. Pick your favorite neighborhood
3. Sort by "Price per SQFT" to find deals
4. Check Days on Market (longer = more motivated seller)

### For Renters (Buy-to-Rent)
1. Look for Cap Rate > 4%
2. GRM < 15x
3. Compare to neighborhood median
4. Check rent-to-price ratio

---

## 🚀 Next Steps (After Demo)

### Add Real NYC Data
```bash
# Load real comparable sales from NYC DOF
python scripts/rolling_comps_loader.py --borough Manhattan

# Load historical sales from ACRIS
python scripts/historical_data_loader.py --all
```

### Build Production UI
- Deploy Streamlit to Streamlit Cloud (free!)
- Or build with Next.js + Tailwind
- Or use Retool/Glide for no-code UI

### Scale the Database
- Supabase free tier: Up to 500MB database
- Upgrade to Pro: $25/month for 8GB
- Current setup: ~50 properties = ~500KB

---

## 💰 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| Supabase | Database + API | **FREE** (up to 500MB) |
| Gemini Flash | Property extraction | **FREE** (60 requests/min) |
| Streamlit | Local UI | **FREE** |
| **TOTAL** | | **$0/month** ✨ |

Compare to original design:
- OpenAI GPT-4: $10-20/month
- Airtable Pro: $20/month
- **You saved $30-40/month!**

---

## 📊 Database Schema

Your Supabase database has 6 tables:

1. **neighborhoods** - 6 NYC neighborhoods with median prices
2. **properties** - 50+ sample listings with ALL details
3. **comparable_sales** - (empty for now, populated by comps_loader)
4. **historical_sales** - (empty for now, populated by historical_loader)
5. **market_metrics** - (for time-series analysis)
6. **buyer_searches** - (for tracking user searches)

All with:
- ✅ Computed columns (Cap Rate, GRM, Price/SQFT calculated automatically)
- ✅ Indexes for fast queries
- ✅ Foreign key relationships
- ✅ Row-level security (can enable auth later)

---

## 🎉 You're Ready to Demo!

Your demo shows:
- ✅ Real-time property search
- ✅ Smart filtering & sorting
- ✅ Investment analysis
- ✅ Market insights
- ✅ AI-powered data extraction
- ✅ Professional UI

**Questions? Issues?**
Check the main README.md or docs/ folder for detailed documentation.

**Enjoy your demo! 🏙️**
