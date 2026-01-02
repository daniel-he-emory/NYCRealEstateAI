# UI/UX Design Specification

Complete design specification for the NYC Real Estate AI user interface, including mockups, user flows, and component specifications.

## Design Principles

1. **Clarity First**: Show only relevant information at each stage
2. **Trust Through Transparency**: Explain all scores and recommendations
3. **Mobile-First**: Optimize for mobile property browsing
4. **Data-Driven**: Visualize market context to build confidence
5. **Fast**: Minimize clicks from search to property details

## Color Palette

### Primary Colors
- **Primary Blue**: #2B6CB0 (trust, professionalism)
- **Success Green**: #38A169 (good deals, high scores)
- **Warning Yellow**: #ECC94B (medium signals)
- **Alert Red**: #E53E3E (high distress, urgent opportunities)

### Neutrals
- **Dark**: #1A202C (text)
- **Medium**: #718096 (secondary text)
- **Light Gray**: #EDF2F7 (backgrounds)
- **White**: #FFFFFF

### Score Colors
- **90-100**: #276749 (Dark Green)
- **80-89**: #38A169 (Green)
- **70-79**: #9AE6B4 (Light Green)
- **60-69**: #ECC94B (Yellow)
- **Below 60**: #FC8181 (Light Red)

## Typography

- **Headlines**: Inter, 24-32px, Bold
- **Subheads**: Inter, 18-20px, SemiBold
- **Body**: Inter, 14-16px, Regular
- **Small/Meta**: Inter, 12px, Regular

---

## User Flow

```
┌─────────────┐
│   Landing   │
│   Search    │
└──────┬──────┘
       │ (Enter search query)
       ▼
┌─────────────┐
│  Results    │
│   List      │
└──────┬──────┘
       │ (Click property)
       ▼
┌─────────────┐
│  Property   │
│   Detail    │
└──────┬──────┘
       │ (Save/Share/Back)
       ▼
┌─────────────┐
│  Saved      │
│ Properties  │
└─────────────┘
```

---

## Screen 1: Search Interface

### Purpose
Allow users to describe their ideal property in natural language without complex forms.

### Layout

```
┌──────────────────────────────────────────────┐
│  NYC Real Estate AI                    [≡]   │
├──────────────────────────────────────────────┤
│                                              │
│      🏙️                                      │
│                                              │
│   Find Your Perfect NYC Home                 │
│   with AI-Powered Recommendations            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Describe your dream home...            │ │
│  │                                        │ │
│  │ Example: "2 bed under $1.8M,          │ │
│  │ elevator, lots of light, near subway  │ │
│  │ in LIC or Manhattan"                  │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│        [    Find Properties    ]             │
│                                              │
│  ───────────── or try ─────────────          │
│                                              │
│  [Budget Buys]  [Investment]  [Luxury]       │
│                                              │
├──────────────────────────────────────────────┤
│  Recent Searches:                            │
│  • 2 bed LIC under $1.5M                     │
│  • 3 bed Manhattan doorman                   │
└──────────────────────────────────────────────┘
```

### Component Specifications

**Main Text Area**:
- Height: 150px
- Placeholder: "Describe your dream home..."
- Character limit: 500
- Auto-resize as user types
- Font: 16px Inter

**CTA Button**:
- Size: Large (full-width on mobile)
- Background: Primary Blue
- Text: "Find Properties" with search icon
- Hover: Darken 10%

**Quick Filters (Pills)**:
- "Budget Buys" → pre-fills "under $1.2M high value"
- "Investment" → pre-fills "high rental yield good ROI"
- "Luxury" → pre-fills "3+ bed doorman parking $2M+"

**Recent Searches**:
- Show last 3 searches
- Clickable to re-run
- Display as simple text links

---

## Screen 2: Results List

### Purpose
Display ranked properties with clear scoring, key details, and seller signals.

### Layout

```
┌──────────────────────────────────────────────┐
│  ← Back to Search              [⋮] Filter    │
├──────────────────────────────────────────────┤
│  Found 12 properties matching your search    │
│  "2 bed under $1.8M, elevator, LIC"         │
│                                              │
│  Sort by: [Fit Score ▼]                      │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ [Property Image]         [♡ Save]     │ │
│  │                                        │ │
│  │ 4610 Center Blvd #1234              92 │ │
│  │ Long Island City                    ⭐  │ │
│  │                                        │ │
│  │ $1,650,000  (was $1,800,000)        🔴 │ │
│  │ 2 BR  2 BA  1,250 sqft                 │ │
│  │                                        │ │
│  │ 🏢 Elevator  👤 Doorman  🏋️ Gym       │ │
│  │                                        │ │
│  │ ⚠️ High Seller Motivation              │ │
│  │ • 8.3% price cut (2 reductions)        │ │
│  │ • 77 days on market                    │ │
│  │                                        │ │
│  │ ✓ 4.2% rent-to-price (above avg)       │ │
│  │                                        │ │
│  │              [View Details]             │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ [Property Image]         [♡ Save]     │ │
│  │                                        │ │
│  │ 535 West 43rd St #15C               87 │ │
│  │ Hell's Kitchen                      ⭐  │ │
│  │                                        │ │
│  │ $1,450,000                             │ │
│  │ 2 BR  2 BA  1,100 sqft                 │ │
│  │                                        │ │
│  │ 🏢 Elevator  👤 Doorman  🅿️ Parking    │ │
│  │                                        │ │
│  │ 🆕 New Listing (5 days)                │ │
│  │                                        │ │
│  │              [View Details]             │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
```

### Component Specifications

**Property Card**:
- Background: White
- Border: 1px solid #E2E8F0
- Border-radius: 8px
- Padding: 16px
- Shadow on hover: 0 4px 12px rgba(0,0,0,0.1)

**Fit Score Badge**:
- Position: Top right
- Size: 48x48px circle
- Background: Score color (see palette)
- Font: 24px bold white text
- Shadow: 0 2px 4px rgba(0,0,0,0.2)

**Price Display**:
- Current price: 20px bold
- Original price (if cut): 16px strikethrough gray
- Price cut %: Red text

**Distress Indicator**:
- Red/yellow/green dot
- Text label: "High/Medium/Low Seller Motivation"
- Expandable details on hover/tap

**Amenity Icons**:
- Size: 20x20px
- Gray when not present
- Primary blue when present
- Max 6 icons shown, "+" for more

**CTA Button**:
- Full width on mobile
- White background, blue border
- "View Details" text

---

## Screen 3: Property Detail

### Purpose
Provide comprehensive property information with market context and seller signals to support decision-making.

### Layout

```
┌──────────────────────────────────────────────┐
│  ← Back to Results              [♡] [↗]      │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │                                        │ │
│  │      [Property Image Gallery]          │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  4610 Center Blvd #1234, LIC                 │
│  Long Island City, Queens 11109          92  │
│                                          ⭐   │
│  $1,650,000  (Originally $1,800,000)         │
│  $1,320/sqft  |  $850/mo HOA                 │
│                                              │
│  ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬       │
│                                              │
│  📊 KEY DETAILS                              │
│  ┌────────────────────────────────────────┐ │
│  │ 2 Bedrooms  2 Bathrooms  1,250 sqft   │ │
│  │ Floor 24 (High floor)  South facing    │ │
│  │ Built: 2015 (9 years old)              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ✨ AMENITIES                                │
│  ┌────────────────────────────────────────┐ │
│  │ ✓ Elevator         ✓ Doorman          │ │
│  │ ✓ Gym              ✓ Roof Deck        │ │
│  │ ✓ Pet Friendly     ✓ In-Unit Laundry  │ │
│  │ ✗ Parking                              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  🎯 WHY THIS MATCHES (Score: 92/100)        │
│  ┌────────────────────────────────────────┐ │
│  │ Price Match          ████████░  40/40  │ │
│  │ HOA Cost             ███████░░  18/20  │ │
│  │ Commute              ████████░  14/15  │ │
│  │ Amenities            ████████░  15/15  │ │
│  │ Seller Motivation    ██████░░░   8/10  │ │
│  │                                        │ │
│  │ ✓ Under budget by $150K                │ │
│  │ ✓ 7 min walk to 7/E/M trains          │ │
│  │ ✓ Has elevator & doorman (required)    │ │
│  │ ⚠ Price cut indicates negotiation room │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  💰 VALUATION CONTEXT                        │
│  ┌────────────────────────────────────────┐ │
│  │ Rent-to-Price Ratio: 4.2%       ✓     │ │
│  │   vs. LIC average: 3.8%               │ │
│  │   → Above average investment value     │ │
│  │                                        │ │
│  │ Price per SQFT: $1,320          ✓     │ │
│  │   vs. LIC median: $1,180              │ │
│  │   → 12% premium (high floor, views)   │ │
│  │                                        │ │
│  │ HOA as % of Price: 0.62%        ✓✓    │ │
│  │   Grade: Excellent                     │ │
│  │   Annual HOA: $10,200 (very low)      │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  🔴 SELLER SIGNALS (High Motivation)         │
│  ┌────────────────────────────────────────┐ │
│  │ Original Price:     $1,800,000         │ │
│  │ Current Price:      $1,650,000 ↓       │ │
│  │ Total Reduction:    $150,000 (8.3%)    │ │
│  │                                        │ │
│  │ Price Cuts: 2 reductions in 77 days    │ │
│  │ • Oct 15: $1,800,000 → $1,750,000      │ │
│  │ • Nov 20: $1,750,000 → $1,650,000      │ │
│  │                                        │ │
│  │ Days on Market: 77 days                │ │
│  │   vs. LIC average: 52 days            │ │
│  │                                        │ │
│  │ 💡 Interpretation:                     │ │
│  │ Multiple price cuts and extended time  │ │
│  │ suggest highly motivated seller.       │ │
│  │ Strong negotiation opportunity.        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  📍 LOCATION & COMMUTE                       │
│  ┌────────────────────────────────────────┐ │
│  │ [Mini Map]                             │ │
│  │                                        │ │
│  │ 🚇 Nearest Subway: 7 min walk          │ │
│  │    7, E, M lines                       │ │
│  │                                        │ │
│  │ Commute Times:                         │ │
│  │ • Midtown Manhattan: 15 min            │ │
│  │ • Financial District: 25 min           │ │
│  │ • Brooklyn: 30 min                     │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  📋 FULL DESCRIPTION                         │
│  ┌────────────────────────────────────────┐ │
│  │ Stunning 2BR/2BA with floor-to-ceiling │ │
│  │ windows and breathtaking Manhattan     │ │
│  │ skyline views. Modern kitchen with     │ │
│  │ Bosch appliances, marble bathrooms,    │ │
│  │ in-unit W/D. Building amenities        │ │
│  │ include 24hr doorman, fitness center,  │ │
│  │ roof deck, resident lounge.            │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  📊 MARKET COMPARISON                        │
│  ┌────────────────────────────────────────┐ │
│  │ [Chart: LIC Price Trend 2020-2025]     │ │
│  │                                        │ │
│  │ Recent Comparable Sales:               │ │
│  │ • 4610 Center #1156: $1.7M (Dec '24)  │ │
│  │ • 4620 Center #2234: $1.65M (Nov '24)  │ │
│  │ • 4640 Center #834: $1.55M (Oct '24)   │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  🔗 LISTING SOURCE                           │
│  [ View on StreetEasy → ]                    │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  [  Save Property  ]  [  Contact  ]   │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
```

### Component Specifications

**Image Gallery**:
- Full-width carousel
- Height: 300px on mobile, 500px on desktop
- Swipe/arrow navigation
- Thumbnails below on desktop

**Score Breakdown**:
- Visual progress bars for each component
- Color-coded (green = good score)
- Explanatory text for each factor
- Total score prominent

**Valuation Context Cards**:
- Green ✓ for favorable
- Red ✗ for unfavorable
- Compare to neighborhood average
- Explain what it means

**Seller Signals Timeline**:
- Chronological price cuts
- Visual timeline
- Calculate total reduction
- Interpretation section

**Market Comparison Chart**:
- Line chart showing price trends
- Highlight current listing price
- Show comparable sales
- Time range: last 12 months

---

## Screen 4: Add Property (Admin/Power User)

### Purpose
Allow manual or URL-based property entry for database updates.

### Layout

```
┌──────────────────────────────────────────────┐
│  ← Back                                      │
├──────────────────────────────────────────────┤
│                                              │
│  Add New Property                            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Listing URL                            │ │
│  │ ┌──────────────────────────────────┐   │ │
│  │ │ https://streeteasy.com/...       │   │ │
│  │ └──────────────────────────────────┘   │ │
│  │         [ Auto-Extract Data ]          │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ─────────── or enter manually ───────────   │
│                                              │
│  Address *                                   │
│  ┌──────────────────────────────────────┐   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Neighborhood *                              │
│  ┌──────────────────────────────────────┐   │
│  │ [Select from dropdown ▼]             │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Price *                    HOA/mo           │
│  ┌──────────────┐          ┌──────────────┐ │
│  │ $            │          │ $            │ │
│  └──────────────┘          └──────────────┘ │
│                                              │
│  Bedrooms *    Bathrooms *    SQFT *         │
│  ┌─────┐      ┌─────┐       ┌─────────┐    │
│  │     │      │     │       │         │    │
│  └─────┘      └─────┘       └─────────┘    │
│                                              │
│  Amenities                                   │
│  ┌────────────────────────────────────────┐ │
│  │ ☑ Elevator      ☑ Doorman             │ │
│  │ ☐ Parking       ☑ Gym                 │ │
│  │ ☑ Roof Deck     ☑ Pet Friendly        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Description                                 │
│  ┌──────────────────────────────────────┐   │
│  │                                      │   │
│  │                                      │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  [        Save Property        ]             │
│                                              │
└──────────────────────────────────────────────┘
```

### Component Specifications

**URL Auto-Extract**:
- Input field for listing URL
- "Auto-Extract Data" button
- Loading spinner during extraction
- Populate form fields on success
- Error handling with retry option

**Form Validation**:
- Required fields marked with *
- Real-time validation
- Error messages below fields
- Disable submit until valid

---

## Responsive Breakpoints

### Mobile (< 768px)
- Single column layout
- Full-width cards
- Stacked property details
- Bottom sheet for filters
- Sticky CTA buttons

### Tablet (768px - 1024px)
- 2-column property grid
- Side-by-side detail sections
- Sidebar filters

### Desktop (> 1024px)
- 3-column property grid
- Sticky sidebar for filters
- Expanded detail views
- Hover interactions

---

## Interaction Patterns

### Loading States
- Skeleton screens while fetching data
- Progress indicator for search parsing
- Shimmer effect on cards

### Empty States
- No results: Suggest broadening criteria
- No saved properties: Call to action to start searching
- Error states: Clear error message + retry option

### Micro-interactions
- Card hover: Slight elevation + shadow
- Score badge pulse on first view
- Save button: Heart fill animation
- Success feedback: Green checkmark toast

---

## Accessibility

### WCAG 2.1 AA Compliance
- Color contrast ratio ≥ 4.5:1 for text
- Keyboard navigation throughout
- ARIA labels for all interactive elements
- Focus indicators on all interactive elements
- Alt text for all images

### Screen Reader Support
- Semantic HTML (header, nav, main, article)
- Descriptive link text
- Form labels properly associated
- Skip to content link

---

## Data Visualization Components

### Price Trend Chart
- Library: Chart.js or Recharts
- Type: Line chart
- X-axis: Time (months/quarters)
- Y-axis: Price per sqft
- Show: Neighborhood average + current property
- Interactive tooltips

### Score Breakdown
- Type: Horizontal bar chart
- Max value: Points available
- Color: Green gradient
- Labels: Component name + score

### Neighborhood Comparison
- Type: Radar chart or table
- Metrics: Price, rent ratio, days on market
- Compare: Selected property vs neighborhood

---

## Performance Targets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Lighthouse Score: > 90
- Image optimization: WebP format, lazy loading
- API response caching

---

## Error Handling & Edge Cases

### Search Errors
- "No properties match your criteria"
  → Suggest: Remove filters or expand price range
- "Search too vague"
  → Show examples of good searches

### Property Detail Errors
- Missing data fields
  → Show "Not available" or estimate icon
- External listing link broken
  → Show cached description, warn user

### Network Errors
- Offline mode: Show cached results
- API timeout: Retry with exponential backoff
- Rate limiting: Queue requests

---

## Implementation Priority

### Phase 1 (MVP):
1. Search interface
2. Results list with basic cards
3. Detail view with key metrics
4. Basic responsive design

### Phase 2 (Enhanced):
1. Advanced filtering
2. Saved properties
3. Market comparison charts
4. Neighborhood pages

### Phase 3 (Full):
1. User accounts
2. Alerts for new matches
3. Comparative analysis
4. Agent contact integration

---

## Sample Component Code (React/Retool)

### Property Card Component

```jsx
function PropertyCard({ property, fitScore, onClick }) {
  const priceChange = property.originalPrice - property.currentPrice;
  const hasPriceCut = priceChange > 0;

  return (
    <div className="property-card" onClick={onClick}>
      <div className="card-header">
        <img src={property.imageUrl} alt={property.address} />
        <div className="fit-score" style={{background: getScoreColor(fitScore)}}>
          {fitScore}
        </div>
        <button className="save-btn">♡</button>
      </div>

      <div className="card-body">
        <h3>{property.address}</h3>
        <p className="neighborhood">{property.neighborhood}</p>

        <div className="price">
          <span className="current">${formatPrice(property.currentPrice)}</span>
          {hasPriceCut && (
            <>
              <span className="original">${formatPrice(property.originalPrice)}</span>
              <span className="cut-badge">-{Math.round(priceChange/property.originalPrice*100)}%</span>
            </>
          )}
        </div>

        <div className="specs">
          {property.bedrooms} BR · {property.bathrooms} BA · {property.sqft} sqft
        </div>

        <div className="amenities">
          {property.hasElevator && <Icon name="elevator" />}
          {property.hasDoorman && <Icon name="doorman" />}
          {property.hasGym && <Icon name="gym" />}
        </div>

        {property.distressFlag === 'High' && (
          <div className="distress-alert">
            ⚠️ High Seller Motivation
            <ul>
              <li>{Math.round(property.totalCutPercent)}% price cut ({property.priceCutCount} reductions)</li>
              <li>{property.daysOnMarket} days on market</li>
            </ul>
          </div>
        )}

        {property.rentToPriceRatio > 4 && (
          <div className="value-indicator">
            ✓ {property.rentToPriceRatio}% rent-to-price (above avg)
          </div>
        )}
      </div>

      <button className="view-details-btn">View Details</button>
    </div>
  );
}
```

---

## Next Steps

1. Review design with stakeholders
2. Create high-fidelity mockups in Figma
3. Build component library in Retool/Glide
4. User testing with 5-10 target users
5. Iterate based on feedback

For implementation details, see `IMPLEMENTATION.md`.
