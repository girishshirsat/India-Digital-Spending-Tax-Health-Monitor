# Data Cleaning Log

This log lists every cleaning fix for the PhonePe, GST and CPI datasets, with
the reason and the number of rows affected. The cleaning code is in
`src/clean/`, and the output files are in `data/processed/`.

## All datasets

| What we did | Why | Rows affected |
|---|---|---|
| Normalized state names (lowercase, `and` instead of `&`, no hyphens) | The same state is written differently in each source | PhonePe 36 states, GST 36, CPI 35 |
| Added 5 rows to `state_mapping.csv` (3 for NDAP, 2 for CPI) | Dadra & Nagar Haveli and Daman & Diu must become one state, and Other Territory must be dropped | 5 mapping rows |
| Built one list of 36 state names (`dim_state`) | Every table uses the same names, so they can be joined | 36 states |

## PhonePe

| What we did | Why | Rows affected |
|---|---|---|
| Combined 1,008 JSON files (36 states x 28 quarters) into one table | One tidy table with `state, year, quarter, txn_type, count, amount` | 5,034 by-type rows (6 fewer than 5,040) |
| Kept the 6 Lakshadweep rows that have no "Financial Services" type | The source has no activity of that type for 2018 Q1 to 2020 Q1, so we did not invent a zero | 6 state-quarters have 4 types instead of 5 |
| Summed the types into one row per state-quarter | One definition of the total for every later step | 1,008 rows, 0 nulls, 0 zero or negative values, 0 duplicates |
| Flagged big quarter-on-quarter drops with `big_drop` (below -30%) | These look like real events, so we flag them and do not delete them | 6 flagged: Chandigarh 2023 Q1, Goa 2020 Q2, Jammu & Kashmir 2019 Q3 and Q4, Manipur 2023 Q1 and Q2 |

## GST

| What we did | Why | Rows affected |
|---|---|---|
| Dropped rows with `state_code == 97` | Code 97 is Other Territory. 12 of these rows carry the name West Bengal by mistake | 206 rows (194 Other Territory + 12 mislabelled West Bengal) |
| Merged Dadra & Nagar Haveli and Daman & Diu by summing counts | PhonePe treats them as one state. The filing percentage is never summed | 7,622 rows to 7,416 |
| Kept only 2018 to 2024 | This is the PhonePe window | 1,368 rows dropped |
| Converted months to calendar quarters and summed the counts | PhonePe quarters are calendar quarters. The financial-year column is not used | 6,048 rows to 2,016 (36 states x 28 quarters x 2 return types) |
| Recomputed `filing_pct` as `on_time / eligible x 100` from the summed counts | Percentages cannot be added or averaged. It is empty where eligible taxpayers = 0 | 1,998 valid values |
| Set a negative `on_time` value to empty, set `filing_pct` to empty and flagged it (`invalid_negative`) | A count of taxpayers cannot be negative, and a 0 would look like a real number | 1 row: Lakshadweep 2020 Q4, GSTR-3B |
| Flagged a quarter where eligible taxpayers = 0 but returns filed above 0 (`suspect_zero_eligible`) | The zero looks like a placeholder, so the percentage cannot be trusted. `total_filed` is kept | 1 row (11 monthly rows before summing) |
| Kept empty values empty and did not fill them | The source has no data for those months | 6 rows have no `total_filed`, all Ladakh |

## CPI

| What we did | Why | Rows affected |
|---|---|---|
| Used the committed snapshot instead of the 91 MB Excel file | The Excel file is not on GitHub, so the snapshot keeps the pipeline repeatable | 3,813 rows used |
| Quarterly CPI = average of the available months, empty when fewer than 2 months exist | A quarter with too little data is not reliable | 66 quarter values empty |
| Kept missing quarters absent and did not create values | These quarters were never reported | 3 absent rows: Nagaland, Puducherry and Manipur, 2020 Q2 |
| Calculated yearly inflation (`cpi_yoy`) by comparing the same quarter one year earlier | Removes seasonal effects. It uses a merge by year and quarter, not `shift` | 1,050 valid values out of 1,293 |
| Left Arunachal Pradesh `cpi_yoy` empty | Only 10 of 106 months are valid, with no usable year-on-year pair | 30 quarters |
| Left Ladakh without CPI | The source has no Ladakh data | 0 rows in the final table |
| Averaged the yearly inflation rates of Dadra & Nagar Haveli and Daman & Diu, with equal weights | Their index levels are about 10 points apart, so averaging the levels would invent a number. Equal weights are our choice | 1,293 rows to 1,257 |
| Kept 2018 to 2024 and flagged negative `cpi_yoy` (`cpi_yoy_negative`) | Negative values are kept, because we cannot confirm they are errors | 977 final rows, 9 flagged |
| Kept Daman & Diu's negative inflation from 2018 Q4 to 2019 Q3 | It falls while Dadra & Nagar Haveli does not, so it may be a source quirk. We cannot prove that | 4 quarters. It also pulls down the combined state in those quarters |

## Known limitations

- **Ladakh:** its monthly GST values are empty from July 2017 to February 2020, because it was not yet a separate territory. After summing, 6 rows have no `total_filed`. It has no CPI at all, so it has no real growth.
- **Arunachal Pradesh:** `cpi_yoy` is empty for every quarter, so real growth is empty for it. Its PhonePe and GST data stay in the tables.
- **2020 Q2:** April and May 2020 are missing in the CPI source for all states, so yearly inflation is empty for 2020 Q2 and 2021 Q2 in almost every state.
- **Different measures:** PhonePe gives rupees, and GST gives filing counts, not rupees.
- **GST eligible taxpayers:** the quarterly `eligible` is the sum of 3 months, so the same taxpayer is counted up to 3 times. The filing percentage is still a fair share, because `on_time` is summed the same way.
- **Empty means unknown, not zero.** Empty values are never filled.