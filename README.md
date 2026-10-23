# India Digital Spending & Tax Health Monitor

How digital payments, GST filing and prices relate across Indian states, 2018 to 2024.

**Status:** Phase 0 (feasibility) complete. Verdict: GO. See `docs/feasibility.md`.

## Question
Do states where UPI spending grows fast also show matching growth in GST filings, after adjusting for inflation?

## Planned metrics
- **Real growth** = payment growth minus CPI inflation.
- **Divergence score** = z-score of UPI amount YoY growth minus z-score of GST total-filed YoY growth, per state per quarter. States with |score| > 1.5 are flagged.
- **On-time GST filing %** as a separate tax-health indicator.

## Data sources
| Source | Used for | Level |
|---|---|---|
| PhonePe Pulse (GitHub, master branch) | UPI count and amount | State, quarterly |
| NDAP GST returns | Filing counts, on-time split | State, monthly |
| MoSPI CPI (base 2012) | Inflation adjustment | State, monthly |

## Planned stack
Python, pandas, PostgreSQL (local + Neon), SQL, Streamlit, Tableau Public, Power BI, GitHub Actions.

## Limitations
- Association, not causation.
- PhonePe is roughly 45% of UPI volume.
- GST registration state is not the spending state.
- GST data is filing counts, not rupees.
- PhonePe data used here ends at 2024 Q4.

## Setup
1. `python -m venv venv` and activate it.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your database URLs.

## License
MIT. Data belongs to its original publishers.

Author: Girish Shirsath, <girishshisath2004@gmail.com>