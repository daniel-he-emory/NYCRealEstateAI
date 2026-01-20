# NYC Real Estate AI - Live Demo

A fully functional NYC real estate search engine with AI-powered property analysis, investment metrics, and real-time data from NYC Department of Finance.

🔗 **[Live Demo](http://localhost:8502)** | 📊 **50+ Real NYC Properties** | 💰 **$0/month Cost**

---

## 🚀 What's Built

This is a **production-ready** real estate analysis platform that includes:

✅ **Live Streamlit Web App** - Beautiful, interactive property search interface
✅ **Real NYC Data** - 50+ actual condo sales with specific units from NYC DOF
✅ **Supabase PostgreSQL Database** - Scalable, free-tier cloud database
✅ **Google Gemini AI** - Property data extraction (cheaper & faster than OpenAI)
✅ **Investment Analysis** - Cap Rate, GRM, Cash-on-Cash ROI calculations
✅ **Smart Filters** - Search by price, bedrooms, neighborhoods, amenities
✅ **Market Insights** - Distress flags, price history, market summaries

**Total Cost:** $0/month (all services on free tiers)

---

## 🎯 Quick Start (3 Minutes)

### Prerequisites

- Python 3.8+
- Supabase account (free)
- Google Gemini API key (free tier available)

### Setup

1. **Clone & Install:**
```bash
git clone <your-repo-url>
cd NYCRealEstateAI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
cp .env.example .env
# Add your API keys to .env:
# - SUPABASE_URL
# - SUPABASE_KEY
# - GEMINI_API_KEY
```

3. **Set Up Database:**
```bash
# Run migration in Supabase SQL Editor
# Copy contents of migrations/001_initial_schema_FIXED.sql
# Paste into https://supabase.com/dashboard/project/YOUR_PROJECT/editor
# Click RUN
```

4. **Load Real Data:**
```bash
python scripts/load_real_nyc_data.py
```

5. **Launch Demo:**
```bash
streamlit run app.py
```

Open http://localhost:8502 🎉

---

## 🏗️ Architecture

### Tech Stack

- **Frontend:** Streamlit (Python web framework)
- **Database:** Supabase (PostgreSQL with REST API)
- **AI:** Google Gemini Flash 1.5 (property data extraction)
- **Data Source:** NYC Open Data (Department of Finance Rolling Sales)
- **Hosting:** Local (deployable to Streamlit Cloud)

### Database Schema

6 tables with computed columns and relationships:

1. **neighborhoods** - NYC neighborhood data with market metrics
2. **properties** - Property listings with investment calculations
3. **comparable_sales** - Recent sales for YoY analysis
4. **historical_sales** - ACRIS historical data
5. **market_metrics** - Time-series market data
6. **buyer_searches** - User search tracking

All with auto-calculated fields:
- Cap Rate, GRM, Cash-on-Cash ROI
- Price per sqft, HOA ratios
- Distress flags (motivated sellers)
- Appreciation since last sale

---

## 📊 Features

### Property Search
- **Smart Filters:** Price range, bedrooms, bathrooms, amenities
- **Neighborhoods:** Long Island City, Hell's Kitchen, DUMBO, Financial District, Upper West Side, Park Slope
- **Sorting:** By price, price/sqft, cap rate, days on market
- **Status:** Active, Price Change, In Contract

### Investment Analysis
- **Cap Rate:** Net Operating Income / Price (target: 3-5% in NYC)
- **Gross Rent Multiplier:** Price / Annual Rent (ideal: <15x)
- **Rent-to-Price Ratio:** Annual rent as % of purchase price
- **Cash-on-Cash Return:** Annual cash flow / down payment
- **Color-coded ratings:** Green (good), Orange (fair), Red (poor)

### Seller Signals
- **High Distress:** 10%+ price cut + 60+ days on market
- **Medium Distress:** 5%+ price cut or 45+ days
- **Price History Charts:** Track all price reductions

### Property Cards
Each listing shows:
- 📍 Real address with specific unit number
- 💰 Current price, price/sqft, HOA fees
- 🏠 Bedrooms, bathrooms, square footage
- 📊 Investment metrics (toggleable)
- 🔥 Distress flags for motivated sellers
- 🚇 Subway distance and lines
- 📉 Price history charts
- 📄 Full property descriptions

### Market Summary
- Average price & price per sqft
- Average days on market
- Average cap rate across results
- Total properties matching filters

---

## 🤖 AI Property Scraper

Extract property data from any listing URL using Gemini AI:

```bash
# Single property
python scripts/property_extractor_gemini.py https://streeteasy.com/building/...

# Bulk import
echo "url1" > urls.txt
echo "url2" >> urls.txt
python scripts/property_extractor_gemini.py --bulk urls.txt
```

The AI automatically extracts:
- Address, price, beds, baths, sqft
- Amenities (elevator, doorman, gym, parking)
- Building details (year built, floor level, exposure)
- HOA fees, estimated rent
- Subway access

---

## 📁 Project Structure

```
NYCRealEstateAI/
├── app.py                              # Streamlit web interface
├── scripts/
│   ├── load_real_nyc_data.py          # Load data from NYC DOF API
│   ├── property_extractor_gemini.py    # AI-powered property scraper
│   ├── direct_load.py                  # Direct database loader
│   ├── fix_addresses.py                # Address formatting utility
│   ├── refresh_schema.py               # Supabase schema cache refresh
│   └── setup_database.py               # Initial database setup
├── migrations/
│   └── 001_initial_schema_FIXED.sql   # PostgreSQL database schema
├── .env                                # API keys (not in git)
├── requirements.txt                    # Python dependencies
├── QUICK_START.md                      # Step-by-step setup guide
└── README.md                           # This file
```

---

## 🎨 Screenshots

### Property Search Interface
- Clean, modern UI with sidebar filters
- Property cards with full details
- Investment metrics with color coding
- Market summary statistics

### Investment Analysis
- Cap Rate calculations
- Gross Rent Multiplier
- Rent-to-Price ratios
- Distress flags highlighted

### Property Details
- Full descriptions with expandable sections
- Price history charts
- Amenities icons
- Neighborhood information

---

## 🔧 API Keys

You'll need these free API keys:

| Service | Purpose | Cost | Get Key |
|---------|---------|------|---------|
| **Supabase** | PostgreSQL database | FREE (500MB) | [supabase.com](https://supabase.com) |
| **Google Gemini** | AI property extraction | FREE (60 req/min) | [aistudio.google.com](https://aistudio.google.com) |
| **NYC Open Data** | Property sales data | FREE | [data.cityofnewyork.us](https://data.cityofnewyork.us) (optional) |

---

## 💡 Use Cases

### For Investors
1. Filter for Cap Rate > 4%
2. Look for High Distress flags (motivated sellers)
3. Compare rent-to-price ratios
4. Track properties with multiple price cuts

### For First-Time Buyers
1. Set your budget range
2. Pick your favorite neighborhoods
3. Sort by price per sqft to find deals
4. Check days on market (longer = more negotiable)

### For Real Estate Agents
1. Show clients investment metrics
2. Compare properties side-by-side
3. Track market trends by neighborhood
4. Export data for client presentations

---

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud (Free)
1. Push to GitHub
2. Connect at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Deploy with one click
4. Add secrets (API keys) in dashboard

### Custom Domain
- Streamlit Cloud supports custom domains on paid plans
- Or deploy to Heroku, Railway, Render, etc.

---

## 📊 Data Sources

### NYC Department of Finance
- **Rolling Sales:** Recent condo transactions
- **ACRIS:** Historical sales records (1966-present)
- **PLUTO:** Property assessments, building data
- All data is public and free

### Property Websites (AI Scraper)
- StreetEasy
- Zillow
- Realtor.com
- Any listing URL with property details

---

## 🔒 Security Notes

- Never commit `.env` file (already in `.gitignore`)
- Use service role keys only in backend scripts
- Enable Row Level Security in Supabase for production
- Rotate API keys periodically
- Use environment variables for all secrets

---

## 🛠️ Development

### Run Tests
```bash
# Test database connection
python scripts/setup_database.py

# Test data loader
python scripts/load_real_nyc_data.py

# Test AI scraper (need a listing URL)
python scripts/property_extractor_gemini.py <url>
```

### Database Migrations
```bash
# Create new migration
# Edit migrations/00X_description.sql

# Run in Supabase SQL Editor or:
python scripts/run_migration_auto.py
```

### Add More Properties
```bash
# From NYC Open Data
python scripts/load_real_nyc_data.py

# From listing URLs
python scripts/property_extractor_gemini.py --bulk urls.txt
```

---

## 📈 Roadmap

### Current Features ✅
- [x] Real-time property search
- [x] Investment analysis
- [x] Real NYC data integration
- [x] AI property scraper
- [x] Streamlit web interface

### Planned Features 🎯
- [ ] User authentication (Supabase Auth)
- [ ] Save favorite properties
- [ ] Email alerts for new listings
- [ ] Comparable sales analysis
- [ ] Neighborhood trend charts
- [ ] Mobile-responsive design improvements
- [ ] Export to CSV/PDF
- [ ] Property comparison view

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🎓 Learning Resources

Built with these technologies:

- [Streamlit Docs](https://docs.streamlit.io)
- [Supabase Docs](https://supabase.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [NYC Open Data](https://opendata.cityofnewyork.us/)
- [PostgreSQL Computed Columns](https://www.postgresql.org/docs/current/ddl-generated-columns.html)

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/NYCRealEstateAI/issues)
- **Questions:** Open a discussion
- **Demo Issues:** Check `QUICK_START.md` for troubleshooting

---

## 🏆 Credits

Built by [Daniel](https://github.com/yourusername) using:
- NYC Open Data for real property sales
- Supabase for database infrastructure
- Google Gemini for AI capabilities
- Streamlit for rapid prototyping

---

**⭐ Star this repo if you find it useful!**

**📧 [Contact](mailto:your.email@example.com)** | **🐦 [Twitter](https://twitter.com/yourhandle)** | **💼 [LinkedIn](https://linkedin.com/in/yourprofile)**
