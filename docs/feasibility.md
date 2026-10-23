# Feasibility Check (Phase 0)

**Verdict: GO.** The PhonePe, GST and CPI data can be joined at state x quarter level for 2018 Q1 to 2024 Q4.

## 1. PhonePe Pulse
- Source: GitHub `PhonePe/pulse`, branch **master**, path `data/aggregated/transaction/country/india/state/<state>/<year>/<quarter>.json`.
- Master has `count` and `amount`. Branch `main` has newer years but only `count` (types P2P, Retail, Utility), so it cannot be used for amount growth.
- Maharashtra: all 28 quarters (2018 Q1 to 2024 Q4) load with count and amount.
- All 36 state/UT folders load for 2024 Q4.

## 2. GST filing (NDAP)
- File: `Goods and Service Tax Returns.csv`, downloaded on <download date>.
- 7,828 rows, 12 columns, monthly, July 2017 to January 2026, GSTR-1 and GSTR-3B rows.
- 38 state names: 36 real states/UTs plus "Other Territory" (dropped).
- Filing counts, not rupees.

## 3. State matching
- 35 of 36 PhonePe states match NDAP directly after lowercasing and replacing `-` and `&`.
- The one mismatch: PhonePe has a merged Dadra & Nagar Haveli and Daman & Diu; NDAP has two separate rows. Fix: `src/clean/state_mapping.csv` (sum the two rows, recompute filing % from the summed counts).
- With the mapping, 36 of 36 match (target was 34).

## 4. Overlap window
- All 28 quarters from 2018 Q1 to 2024 Q4 exist in both sources (checked in code).
- Year-over-year growth needs the previous year, so PhonePe growth starts in 2019 Q1. The divergence score covers 2019 Q1 to 2024 Q4 (24 quarters).

## 5. CPI
- State-level CPI exists: `cpi_1520.xlsx`, base 2012=100, monthly, January 2017 to December 2025, 36 states/UTs.
- Used: General index, Combined sector (3,813 rows).
- April and May 2020 are missing for all states; Nagaland, Puducherry and Manipur are also missing June 2020.
- Arunachal Pradesh has only 10 valid months in the window. Decision for cleaning phase: use all-India CPI or exclude it from real growth.
- The Excel file is 91 MB, so it is kept out of Git. A small filtered CSV will be committed later.

## 6. Databases
- Local PostgreSQL 17.7 and Neon PostgreSQL 18.6 both connect from Python through `src/db/connection.py` and `.env`.

## 7. Datasets rejected
- NDAP E-way bills, IGST settlement, digital transactions/BHIM (country level only), tax revenue collection (yearly, rupees).

## 8. Limitations (for README)
- Association, not causation.
- PhonePe is roughly 45% of UPI volume; other apps have no state-level data.
- GST registration state is not the spending state.
- GST data is filing counts, not rupees.
- PhonePe master data ends at 2024 Q4.

## 9. Not checked yet
- RBI NEFT/RTGS and NPCI chargeback files (Module 2). They have no state level and do not affect the Module 1 verdict.