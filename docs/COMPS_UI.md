# Comparable Sales UI Components

UI/UX specifications for displaying year-over-year comparable sales analysis in the NYCRealEstateAI interface.

## Overview

The comps UI provides buyers with instant market intelligence through visual trend indicators, detailed comp tables, and actionable negotiation insights.

---

## Component 1: YoY Trend Badge

### Purpose
Quick visual indicator of market direction on property cards and detail pages.

### Design Specifications

**Position**: Top right of property card, next to fit score badge

**Size**: Compact badge, 80x30px

**Variants**:

#### Rising Market
```
┌────────────────┐
│ ↗ Rising +5.2% │  Green background (#38A169)
└────────────────┘
```

#### Declining Market
```
┌───────────────────┐
│ ↘ Declining -3.8% │  Red background (#E53E3E)
└───────────────────┘
```

#### Stable Market
```
┌──────────────────┐
│ → Stable +1.2%   │  Gray background (#718096)
└──────────────────┘
```

#### Insufficient Data
```
┌─────────────────┐
│ ? Limited Data  │  Light gray (#CBD5E0)
└─────────────────┘
```

### Implementation (React/Retool)

```jsx
function YoYTrendBadge({ yoyPercent, compsCount }) {
  if (compsCount < 3) {
    return (
      <div className="trend-badge insufficient">
        <span>? Limited Data</span>
      </div>
    );
  }

  let variant, icon, label;

  if (yoyPercent > 5) {
    variant = 'rising';
    icon = '↗';
    label = 'Rising';
  } else if (yoyPercent < -5) {
    variant = 'declining';
    icon = '↘';
    label = 'Declining';
  } else {
    variant = 'stable';
    icon = '→';
    label = 'Stable';
  }

  return (
    <div className={`trend-badge ${variant}`}>
      <span className="icon">{icon}</span>
      <span className="label">{label}</span>
      <span className="value">{yoyPercent > 0 ? '+' : ''}{yoyPercent.toFixed(1)}%</span>
    </div>
  );
}
```

### CSS

```css
.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.trend-badge.rising {
  background: #38A169;
}

.trend-badge.declining {
  background: #E53E3E;
}

.trend-badge.stable {
  background: #718096;
}

.trend-badge.insufficient {
  background: #CBD5E0;
  color: #4A5568;
}

.trend-badge .icon {
  font-size: 16px;
}
```

---

## Component 2: Comparable Sales Table

### Purpose
Show top 5-10 recent comparable sales with YoY metrics.

### Design

```
┌─────────────────────────────────────────────────────────────────┐
│ Recent Comparable Sales (6 comps)                              │
├─────────────────────────────────────────────────────────────────┤
│ Unit  Beds/Baths  Sq Ft  Sale Date    Price      PPSF    YoY   │
├─────────────────────────────────────────────────────────────────┤
│ #12B    2/2      1,200   Dec 2024   $1,650,000  $1,375  +6.4% ↗│
│ #8B     2/2      1,150   Nov 2024   $1,550,000  $1,348  +5.1% ↗│
│ #20A    2/2      1,250   Oct 2024   $1,720,000  $1,376  +7.2% ↗│
│ #6D     2/1      1,180   Sep 2024   $1,480,000  $1,254  +4.8% ↗│
│ #18C    2/2      1,220   Aug 2024   $1,620,000  $1,328  +3.9% ↗│
│ #14F    2/2      1,190   Jul 2024   $1,560,000  $1,311  +2.1% →│
├─────────────────────────────────────────────────────────────────┤
│ Median:                               $1,585,000  $1,348        │
│ Average YoY Change:                                      +4.9% ↗│
└─────────────────────────────────────────────────────────────────┘
```

### Implementation (Retool Table Component)

**Columns**:
1. **Unit**: Text, left-aligned
2. **Beds/Baths**: Text, centered, format: "2/2"
3. **Sq Ft**: Number, right-aligned, thousand separator
4. **Sale Date**: Date, "MMM YYYY" format
5. **Price**: Currency, right-aligned, "$1,650,000"
6. **PPSF**: Currency, right-aligned, "$1,375"
7. **YoY**: Percent, right-aligned, color-coded + icon

**Conditional Formatting**:
- YoY > 5%: Green text, ↗ icon
- YoY < -5%: Red text, ↘ icon
- YoY -5% to +5%: Gray text, → icon

**Footer**:
- Show median price and PPSF
- Show average YoY change with trend icon

### Sample Code (React)

```jsx
function CompsTable({ comps }) {
  const sortedComps = comps
    .sort((a, b) => new Date(b.SaleDate) - new Date(a.SaleDate))
    .slice(0, 6);

  const medianPPSF = median(sortedComps.map(c => c.PPSF));
  const avgYoY = average(sortedComps.map(c => c.YoY_PPSF_Change));

  return (
    <div className="comps-table-container">
      <div className="table-header">
        <h3>Recent Comparable Sales</h3>
        <span className="comp-count">({comps.length} comps)</span>
      </div>

      <table className="comps-table">
        <thead>
          <tr>
            <th>Unit</th>
            <th>Beds/Baths</th>
            <th>Sq Ft</th>
            <th>Sale Date</th>
            <th>Price</th>
            <th>PPSF</th>
            <th>YoY</th>
          </tr>
        </thead>
        <tbody>
          {sortedComps.map(comp => (
            <tr key={comp.id}>
              <td>{comp.UnitNumber}</td>
              <td>{comp.Bedrooms}/{comp.Bathrooms}</td>
              <td>{comp.SQFT.toLocaleString()}</td>
              <td>{formatDate(comp.SaleDate, 'MMM YYYY')}</td>
              <td>${comp.SalePrice.toLocaleString()}</td>
              <td>${comp.PPSF.toLocaleString()}</td>
              <td className={getYoYClass(comp.YoY_PPSF_Change)}>
                {comp.YoY_PPSF_Change > 0 ? '+' : ''}
                {comp.YoY_PPSF_Change.toFixed(1)}%
                {getYoYIcon(comp.YoY_PPSF_Change)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan="4">Median:</td>
            <td>${median(sortedComps.map(c => c.SalePrice)).toLocaleString()}</td>
            <td>${medianPPSF.toLocaleString()}</td>
            <td></td>
          </tr>
          <tr>
            <td colSpan="6">Average YoY Change:</td>
            <td className={getYoYClass(avgYoY)}>
              {avgYoY > 0 ? '+' : ''}
              {avgYoY.toFixed(1)}%
              {getYoYIcon(avgYoY)}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

function getYoYClass(yoy) {
  if (yoy > 5) return 'yoy-rising';
  if (yoy < -5) return 'yoy-declining';
  return 'yoy-stable';
}

function getYoYIcon(yoy) {
  if (yoy > 5) return ' ↗';
  if (yoy < -5) return ' ↘';
  return ' →';
}
```

---

## Component 3: PPSF Trend Sparkline

### Purpose
Visual trend line showing PPSF changes over time.

### Design

```
┌────────────────────────────────────────┐
│ Price Per SQFT Trend (12 months)      │
│                                   ╱    │
│                              ╱───╯     │
│                         ╱───╯          │
│                    ╱───╯               │
│               ╱───╯                    │
│          ╱───╯                         │
│ $1,200 ─────────────────────────  +6%  │
│ Jul '24              Jun '25           │
└────────────────────────────────────────┘
```

### Implementation (Chart.js)

```javascript
const ppsfData = comps.map(c => ({
  x: new Date(c.SaleDate),
  y: c.PPSF
})).sort((a, b) => a.x - b.x);

const sparklineConfig = {
  type: 'line',
  data: {
    datasets: [{
      data: ppsfData,
      borderColor: '#2B6CB0',
      borderWidth: 2,
      fill: false,
      pointRadius: 0,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `$${context.parsed.y}/sqft`
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: { unit: 'month' },
        display: true,
        grid: { display: false }
      },
      y: {
        display: true,
        ticks: {
          callback: (value) => `$${value}`
        }
      }
    }
  }
};
```

**Dimensions**: 300px wide × 100px tall (compact sparkline)

**Color Coding**:
- Upward trend (>5% YoY): Green line (#38A169)
- Downward trend (<-5% YoY): Red line (#E53E3E)
- Stable: Blue line (#2B6CB0)

---

## Component 4: Negotiation Insights Card

### Purpose
Actionable recommendations based on YoY trends.

### Design

```
┌─────────────────────────────────────────────────────────┐
│ 💡 Negotiation Insights                                 │
├─────────────────────────────────────────────────────────┤
│ Market Trend:  ↘ Declining -3.2% YoY                   │
│ Your Advantage: ✓ Strong Buyer Leverage                │
│                                                         │
│ Recommended Strategy:                                   │
│ • Start 8-10% below asking price                      │
│ • Emphasize declining comps in offer                  │
│ • Highlight 73 days on market                         │
│ • Request closing cost credits                        │
│                                                         │
│ Comps Analysis:                                         │
│ • 6 recent sales averaging -3.2% YoY                   │
│ • Current listing priced at median (fair)              │
│ • No sales in last 60 days (cooling market)            │
└─────────────────────────────────────────────────────────┘
```

### Logic (Pseudo-code)

```javascript
function generateNegotiationInsights(property) {
  const { AvgCompsYoY_PPSF, CompsPriceVariance, DaysOnMarket, CompsCount } = property;

  let insights = {
    trend: '',
    leverage: '',
    strategy: [],
    analysis: []
  };

  // Determine trend
  if (AvgCompsYoY_PPSF < -5) {
    insights.trend = `↘ Declining ${AvgCompsYoY_PPSF.toFixed(1)}% YoY`;
    insights.leverage = '✓ Strong Buyer Leverage';
    insights.strategy.push('Start 8-10% below asking price');
    insights.strategy.push('Emphasize declining comps in offer');
  } else if (AvgCompsYoY_PPSF > 5) {
    insights.trend = `↗ Rising +${AvgCompsYoY_PPSF.toFixed(1)}% YoY`;
    insights.leverage = '⚠ Limited Negotiation Room';
    insights.strategy.push('Offer at or slightly below ask');
    insights.strategy.push('Consider quick close to lock in price');
  } else {
    insights.trend = `→ Stable ${AvgCompsYoY_PPSF > 0 ? '+' : ''}${AvgCompsYoY_PPSF.toFixed(1)}% YoY`;
    insights.leverage = 'Balanced Market';
    insights.strategy.push('Start 3-5% below asking price');
    insights.strategy.push('Standard negotiation approach');
  }

  // Add days on market leverage
  if (DaysOnMarket > 60) {
    insights.strategy.push(`Highlight ${DaysOnMarket} days on market`);
  }

  // Add pricing variance insight
  if (CompsPriceVariance > 10) {
    insights.strategy.push('Property overpriced vs comps - strong leverage');
  } else if (CompsPriceVariance < -10) {
    insights.strategy.push('Property underpriced - act quickly');
  }

  // Analysis points
  insights.analysis.push(`${CompsCount} recent sales averaging ${AvgCompsYoY_PPSF.toFixed(1)}% YoY`);

  if (CompsPriceVariance < -10) {
    insights.analysis.push('Current listing priced below median (good value)');
  } else if (CompsPriceVariance > 10) {
    insights.analysis.push('Current listing priced above median');
  } else {
    insights.analysis.push('Current listing priced at median (fair)');
  }

  return insights;
}
```

### Implementation (React Component)

```jsx
function NegotiationInsightsCard({ property }) {
  const insights = generateNegotiationInsights(property);

  return (
    <div className="insights-card">
      <div className="card-header">
        <span className="icon">💡</span>
        <h3>Negotiation Insights</h3>
      </div>

      <div className="insight-row">
        <label>Market Trend:</label>
        <span className="value">{insights.trend}</span>
      </div>

      <div className="insight-row">
        <label>Your Advantage:</label>
        <span className="value">{insights.leverage}</span>
      </div>

      <div className="strategy-section">
        <h4>Recommended Strategy:</h4>
        <ul>
          {insights.strategy.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="analysis-section">
        <h4>Comps Analysis:</h4>
        <ul>
          {insights.analysis.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## Component 5: Value vs Comps Indicator

### Purpose
Quick visual showing if property is overpriced, fair, or underpriced vs recent comps.

### Design

```
Listing PPSF:        $1,385
Median Comps:        $1,348
                     ─────
Variance:            +2.7%  [═════════▓░░░░░░] FAIR PRICE
```

**Scale**:
- -20% to -10%: UNDERPRICED (dark green)
- -10% to -5%: Good Value (light green)
- -5% to +5%: FAIR PRICE (gray)
- +5% to +10%: Slightly High (light orange)
- +10% to +20%: OVERPRICED (dark orange)

### Implementation

```jsx
function ValueVsCompsIndicator({ listingPPSF, medianCompsPPSF }) {
  const variance = ((listingPPSF - medianCompsPPSF) / medianCompsPPSF) * 100;

  let label, color;
  if (variance < -10) {
    label = 'UNDERPRICED';
    color = '#276749';
  } else if (variance < -5) {
    label = 'Good Value';
    color = '#38A169';
  } else if (variance < 5) {
    label = 'FAIR PRICE';
    color = '#718096';
  } else if (variance < 10) {
    label = 'Slightly High';
    color = '#DD6B20';
  } else {
    label = 'OVERPRICED';
    color = '#C05621';
  }

  // Progress bar position (centered at 0%, range -20% to +20%)
  const barPosition = Math.max(-20, Math.min(20, variance));
  const barPercent = ((barPosition + 20) / 40) * 100;

  return (
    <div className="value-indicator">
      <div className="values-row">
        <div>
          <label>Listing PPSF:</label>
          <span className="value">${listingPPSF.toLocaleString()}</span>
        </div>
        <div>
          <label>Median Comps:</label>
          <span className="value">${medianCompsPPSF.toLocaleString()}</span>
        </div>
      </div>

      <div className="variance-row">
        <label>Variance:</label>
        <span className="variance">{variance > 0 ? '+' : ''}{variance.toFixed(1)}%</span>
      </div>

      <div className="progress-bar">
        <div className="bar-fill" style={{
          width: `${barPercent}%`,
          backgroundColor: color
        }}></div>
        <div className="marker" style={{ left: '50%' }}></div>
      </div>

      <div className="label" style={{ color }}>
        {label}
      </div>
    </div>
  );
}
```

---

## Mobile Responsive Design

### Property Card (Mobile)
```
┌───────────────────────┐
│ [Photo]         [♡]   │
│                       │
│ $1,800,000     ↗ +5% │
│ 4610 Center Blvd      │
│ Long Island City      │
│                       │
│ 2BR  2BA  1,300 sqft  │
│ 🏢 👤 🏋️              │
│                       │
│ 6 Comps  Avg +5.2% YoY│
│ ✓ Rising Market       │
│                       │
│ [View Details]        │
└───────────────────────┘
```

**YoY Badge**: Positioned next to price, compact version
**Comps Summary**: Single line below amenities
**No sparkline on cards** (detail page only)

---

## Accessibility

### ARIA Labels
```html
<div
  className="trend-badge rising"
  aria-label="Rising market with 5.2% year over year price increase"
>
  ↗ Rising +5.2%
</div>
```

### Screen Reader Announcements
- "Property located in rising market, up 5.2% year over year based on 6 comparable sales"
- "Listing priced 2.7% above median comps, considered fair value"
- "Negotiation advantage: Strong buyer leverage in declining market"

### Keyboard Navigation
- Tab through comps table rows
- Arrow keys to navigate sparkline data points
- Enter to expand/collapse insights card

---

## Performance Optimization

### Lazy Loading
- Load sparkline chart only when detail page visible
- Defer comps table rendering until user scrolls to section
- Paginate comps if >20 (show 10, "Load More" button)

### Caching
- Cache YoY calculations for 24 hours
- Refresh comps data weekly
- Store median PPSF in property record to avoid recalculating

---

## Testing Checklist

- [ ] YoY badge displays correct variant (Rising/Declining/Stable)
- [ ] Comps table sorts by sale date descending
- [ ] Sparkline renders correctly on all screen sizes
- [ ] Negotiation insights update when YoY changes
- [ ] Value indicator bar position accurate
- [ ] Mobile layout stacks components properly
- [ ] Tooltips show on hover for all metrics
- [ ] Screen reader announces trends correctly
- [ ] Colors meet WCAG AA contrast standards

---

## Example Screenshots

### Property Detail with Comps Section

```
┌─────────────────────────────────────────────────────────────────┐
│ 4610 Center Blvd #15C, LIC                              92   ↗ │
│ $1,800,000                                              ★  +5% │
│ ───────────────────────────────────────────────────────────────│
│                                                                 │
│ 📊 Comparable Sales Analysis                                   │
│                                                                 │
│ Recent Comps (6)                         PPSF Trend (12 mo)    │
│ ┌──────────────────────────┐           ┌────────────────────┐ │
│ │ Unit   Date    Price  YoY│           │           ╱        │ │
│ │ #12B  Dec'24  $1.65M +6%│           │      ╱───╯         │ │
│ │ #8B   Nov'24  $1.55M +5%│           │ ╱───╯              │ │
│ │ #20A  Oct'24  $1.72M +7%│           │                    │ │
│ │ #6D   Sep'24  $1.48M +5%│           └────────────────────┘ │
│ │ #18C  Aug'24  $1.62M +4%│                   +5.2% YoY      │
│ │ Median: $1,585K  +5.2% │                                   │
│ └──────────────────────────┘                                 │
│                                                                 │
│ 💡 Negotiation Insights                                        │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Market: Rising +5.2% YoY                                  │  │
│ │ Leverage: Limited Negotiation Room                        │  │
│ │                                                            │  │
│ │ Strategy:                                                  │  │
│ │ • Offer at or slightly below ask                          │  │
│ │ • Consider quick close                                     │  │
│ │ • Priced fairly vs comps (+2.7%)                          │  │
│ └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

This comprehensive comps UI gives users instant market intelligence to make data-driven offers with confidence.
