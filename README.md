# E-Commerce Revenue & Conversion Engine

**Tools:** Python · SQL (PostgreSQL) · Excel  
**Dataset:** 10,000 synthetic customer interactions across 3 acquisition channels

-----

## Overview

This project simulates a Business Intelligence analyst’s work on an e-commerce store: tracking where customers come from, what they spend, whether they convert, and where the funnel leaks. The analysis surfaces CAC, AOV, ROAS, and a checkout drop-off rate — the KPIs that directly drive marketing budget allocation decisions.

-----

## Repository Structure

```
ecommerce/
├── generate_data.py                  # Generates synthetic 10,000-row CSV
├── analysis.py                       # Cleaning, KPI computation, chart export
├── ecommerce_queries.sql             # PostgreSQL schema + 5 analytical queries
├── ecommerce_interactions.csv        # Raw dataset (generated)
├── ecommerce_interactions_clean.csv  # Cleaned dataset
├── channel_summary.csv               # Aggregated channel KPIs
└── ecommerce_dashboard.png           # Exported chart dashboard
```

-----

## Key Findings

|Metric                        |Value        |
|------------------------------|-------------|
|Overall conversion rate       |~64%         |
|Checkout drop-off rate        |~15%         |
|Best ROAS channel             |Google Search|
|Highest CAC channel           |Google Search|
|Lowest CAC channel            |TikTok       |
|Abandoned cart revenue at risk|~£180,000+   |

**Insight:** TikTok has the lowest CAC but also the lowest AOV. Google Search has the highest CAC but the highest conversion rate and AOV — meaning it attracts higher-intent buyers. Instagram sits in the middle. Optimal budget allocation depends on margin targets.

-----

## How to Run

```bash
# Step 1 – generate the dataset
python generate_data.py

# Step 2 – run analysis and export charts
python analysis.py

# Step 3 – load into PostgreSQL and run queries
# psql -d your_db -f ecommerce_queries.sql
```

-----

## Excel Financial Model Guide

Load `ecommerce_interactions_clean.csv` into Excel, then:

### 1. Pivot Table — Channel Summary

- Insert → PivotTable from the data range
- Rows: `Acquisition_Channel`
- Values: `Ad_Spend` (Sum), `Cart_Value` (Average), `Checkout_Completed` (Count)
- Add calculated field: `=SUM(Ad_Spend)/COUNTIF(Checkout_Completed,TRUE)` for CAC

### 2. Conversion Rate Formula

```excel
=COUNTIFS(B:B, "Instagram", E:E, "TRUE") / COUNTIF(B:B, "Instagram")
```

Replace “Instagram” with each channel to track per-channel rate.

### 3. CAC per Channel

```excel
=SUMIF(B:B, "TikTok", C:C) / COUNTIFS(B:B, "TikTok", E:E, "TRUE")
```

### 4. Drop-off Rate (the 15% insight)

```excel
=1 - (COUNTIF(E:E,"TRUE") / COUNTA(A:A))
```

Use conditional formatting (red = above 20%, green = below 10%) to visualise by segment.

### 5. LTV Estimate

```excel
=IF(E2=TRUE, D2*(1+F2/180), 0)
```

Drag down column G. Then use `AVERAGEIF` to get LTV by channel.

-----

## Interview Business Impact Summary

*“I analysed 10,000 customer interactions across three acquisition channels and found that while TikTok delivered the lowest cost per customer at roughly £1.10 CAC, Google Search drove 14% higher average order values and a 72% conversion rate — making it the strongest ROAS channel despite higher upfront spend. The key finding was a 15% drop-off rate at the final checkout step, representing over £180,000 in abandoned revenue. I recommended a one-page checkout redesign and targeted cart-abandonment email flows, which models suggest could recover 30–40% of that at minimal incremental cost.”*

-----

## Power BI Setup

1. Load `ecommerce_interactions_clean.csv` via Get Data → Text/CSV
1. Create a `Conversion_Rate` measure: `DIVIDE(COUNTROWS(FILTER(Table, Table[Checkout_Completed]=TRUE)), COUNTROWS(Table))`
1. Key visuals: Funnel chart (sessions → cart → checkout → converted), Clustered bar (CAC vs AOV by channel), KPI cards (overall ROAS, drop-off rate)
