# Data Sources

## 1. PhonePe Pulse (automatic)
- Source:https://api.github.com/repos/PhonePe/pulse/contents/data/aggregated/transaction/country/india/state?ref=master
- How to get it: `python -m src.ingest.run_all`
- Saved in: data/raw/phonepe
- Files: 1,008 (36 states x 28 quarters), downloaded 2026-10-25

## 2. NDAP GST returns (manual download)
- Website: https://ndap.niti.gov.in/catalogue?sectors=2&search=Variables%2CDatasetInfo&query=*&domain=ndap
- Dataset name:Goods and Service Tax Returns
- Steps:
  1. Open the NDAP link above and search for the dataset "Goods and Service Tax Returns".
  2. Select all states and union territories (check).
  3. Select all months available, July 2017 to January 2026 (check).
  4. Select both return types, GSTR-1 and GSTR-3B (check).
  5. Select all columns: eligible taxpayers, filed by due date, filed after due date, total filed, filing % (check).
  6. Click Download and choose CSV format (check).
- Save the file as: Goods and Service Tax Returns
- Save it in: data/raw/ndap_gst
- Expected: 7828 rows, 12 columns
- Downloaded on: 2026-10-22

## 3. MoSPI state CPI (manual download)
- Website: https://esankhyiki.mospi.gov.in/macroindicators?product=cpi
- Dataset name: Consumer Price Index
- Steps:
  1. Open the MoSPI link above and choose the Consumer Price Index (CPI) product.
  2. Select base year 2012 (check).
  3. Select all states and all months from January 2017 to December 2025 (check).
  4. Keep all sectors (Rural, Urban, Combined) and all groups. We filter later in code (check).
  5. Click Download and choose Excel (.xlsx) format (check).
- Save the file as: cpi_1520.xlsx
- Save it in: data/raw/cpi (git-ignored, do not commit)
- Expected: 213834 rows, 11 columns
- Filter we use: General, General-Overall, Combined
- Downloaded on: 2026-10-23
- Small committed copy: data/snapshot/cpi_general_combined.csv (3,813 rows)

## 4. Check your files
Run `python -m src.ingest.run_all`. It logs row counts for each source.
- NDAP file missing: the run stops with an error.
- CPI Excel missing: the run uses `data/snapshot/cpi_general_combined.csv` (3,813 rows) and logs a warning.