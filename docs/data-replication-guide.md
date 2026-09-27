# Data Replication & Query Specification Guide

This document records the exact data provenance, web scraping specifications, spreadsheet transformations, and cleaning pipeline used to produce the research archive for:
**"Understanding the Relationship Between Pokémon Type and its Battle Role Using Official Performance Statistics: Pokémon Database, 2008–2025"** (CSD105 Data Science, Ahmedabad University).

---

## 1. Source Database Specifications

- **Original Primary Repository**: Pokémon Database (PokéBase / Pokémon Pokédex)
- **Source Web URL**: [`https://pokemondb.net/pokedex/all`](https://pokemondb.net/pokedex/all)
- **Corresponding Kaggle Dataset (Max Pokémon, Gen I–IX)**: [Complete Pokemon Dataset (Gen I–IX)](https://www.kaggle.com/datasets/mariotormo/complete-pokemon-dataset-gen-i-ix) (Jon Moore / Mario Tormo, 1,219+ entries)
- **Baseline Kaggle Benchmark (Cited in Paper Bibliography)**: [The Complete Pokemon Dataset by Rounak Banik (2017)](https://www.kaggle.com/datasets/rounakbanik/pokemon) (Gen I–VII, 802 Pokémon)
- **Chronological Scope**: Generations I through IX (including regional forms, Mega Evolutions, Primal reversions, and battle forms up to early 2025).
- **Extracted Attributes**:
  - `#`: National Pokédex Index Number (string/integer)
  - `Name`: Official species name and variant identifier (e.g., `Mewtwo Mega Mewtwo X`, `Eternatus Eternamax`)
  - `Type`: Primary and optional secondary elemental classification (separated by line breaks in raw table format)
  - `Total`: Base Stat Total (BST), the integer sum of the six core combat attributes
  - `HP`: Hit Points
  - `Attack`: Physical Attack
  - `Defense`: Physical Defense
  - `Sp. Atk`: Special Attack
  - `Sp. Def`: Special Defence
  - `Speed`: Movement and initiative priority value

---

## 2. Spreadsheet Export & Google Sheets Transformation

1. The HTML table (`table#pokedex`) from `pokemondb.net/pokedex/all` was imported into Google Sheets as **"Pokemon Dataset"**.
2. Because HTML `<br>` tags between dual types translate into carriage return / line break characters (`\r\n` or `\n`), the raw export contained newlines within the `Type` column.
3. The table was exported as a standard CSV titled **`Pokemon Dataset - Sheet1.csv`** (stored in `data/Pokemon Dataset - Sheet1.csv` and mirrored as `data/pokemon_database_raw.csv`).
4. **Initial Row Audit**:
   - The raw CSV contained **1,220 total rows**.
   - Inspection revealed that row 1,220 originated from an extraneous webpage footer containing copyright notice text (`Privacy PolicyAll content & design © Pokémon Database...`) with `NaN` for all six statistical values and Total.
   - Column `0` header was imported as `'9'` (spreadsheet index artifact) and was mapped back to `'#'`.

---

## 3. Automated Cleaning & Transformation Pipeline (`scripts/build_analysis_data.py`)

When running `python scripts/build_analysis_data.py`, the following systematic operations are executed:

1. **Header Stripping**: Trims leading and trailing whitespace across all column names.
2. **Numeric Type Enforcement**: Columns `['Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']` are coerced via `pd.to_numeric(errors='coerce')`.
3. **Missing Value Pruning**: Rows containing nulls in any of the seven numeric columns are dropped:
   ```python
   df_clean = df.dropna(subset=numeric_cols).copy()
   ```
   - **Pre-cleaning Count**: 1,220 rows
   - **Rows Dropped**: 1 row (row index 1,219)
   - **Post-cleaning Count**: 1,219 unique Pokémon entries
4. **Elemental Type Normalization**:
   ```python
   df_clean['Type_Clean'] = df_clean['Type'].astype(str).str.replace('\r\n', '/').str.replace('\n', '/')
   df_clean['Primary_Type'] = df_clean['Type_Clean'].str.split('/').str[0].str.strip()
   df_clean['Secondary_Type'] = df_clean['Type_Clean'].str.split('/').str[1].str.strip().fillna('None')
   df_clean['Is_Dual_Type'] = df_clean['Secondary_Type'] != 'None'
   ```
5. **Feature Engineering**:
   - $\text{Avg\_Stats} = \frac{\text{HP} + \text{Attack} + \text{Defense} + \text{Sp. Atk} + \text{Sp. Def} + \text{Speed}}{6}$
   - $\text{Physical\_Power} = \frac{\text{Attack} + \text{Defense}}{2}$
   - $\text{Special\_Power} = \frac{\text{Sp. Atk} + \text{Sp. Def}}{2}$
   - $\text{Offensive\_Power} = \frac{\text{Attack} + \text{Sp. Atk}}{2}$
   - $\text{Defensive\_Power} = \frac{\text{Defense} + \text{Sp. Def}}{2}$
   - $\text{Power\_Category} = \text{pd.cut}(\text{Total}, \text{bins}=[0, 300, 450, 600, 1200], \text{labels}=[\text{'Weak'}, \text{'Average'}, \text{'Strong'}, \text{'Legendary'}])$

---

## 4. Replication Runbook

To reproduce all dataset transformations, statistical models, and chart exports from scratch:

```bash
# 1. Clone repository
git clone https://github.com/notnamansinha/the-pokemon-paradox.git
cd the-pokemon-paradox

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Clean raw data and compute analysis JSON
python scripts/build_analysis_data.py

# 4. Render all 10 analytical figures (PNG & PDF)
python scripts/make_charts.py
python scripts/verified_charts.py

# 5. Compile Word Term Paper and PDF
python scripts/build_report.py

# 6. Execute 128 automated mathematical and structural verification tests
python scripts/verify_report.py
```
