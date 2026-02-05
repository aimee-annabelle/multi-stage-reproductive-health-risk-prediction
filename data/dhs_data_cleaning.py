from pathlib import Path

import pandas as pd

# Load your DHS Stata/SPSS file
# Some DHS files contain duplicate value labels, which break categorical conversion.
df = pd.read_stata('../../dataset/RWIR81DT/RWIR81FL.DTA', convert_categoricals=False)

# 1. FILTER: Create the "At Risk" Cohort
# Keep only married women, not on birth control, not currently pregnant
cohort = df[
    (df['v502'].isin([1, 2])) &   # Married/Cohabiting
    (df['v313'] == 0) &           # No contraception
    (df['v213'] == 0)             # Not pregnant
].copy()

# 2. CREATE TARGET: Define Infertility (The "Y") - Comprehensive Approach
# Handle special codes that mean "don't know" or invalid data
v215 = cohort['v215']  # months since last birth
v529 = cohort['v529']  # months since last sex
v531 = cohort['v531']  # time since last sex (days/weeks - check codebook)
v222 = cohort['v222']  # months since first cohabitation
v012 = cohort['v012']  # current age
v511 = cohort['v511']  # age at first marriage/cohabitation

# Filter out special codes (995-999 typically mean DK/missing/not applicable)
valid_v215 = ~v215.isin([995, 996, 997, 998, 999])
valid_v529 = ~v529.isin([995, 996, 997, 998, 999])
valid_v222 = ~v222.isin([995, 996, 997, 998, 999])
valid_v511 = ~v511.isin([95, 96, 97, 98, 99])

# Sexually active in last 12 months (trying to conceive)
sexually_active_12mo = valid_v529 & (v529 <= 12)

# Classification Logic
never_gave_birth = cohort['v201'] == 0
has_birth = cohort['v201'] > 0

# Initialize infertility flag
cohort['is_infertile'] = 0

# === PRIMARY INFERTILITY (never gave birth) ===
# Primary infertility (Option B):
# Never gave birth AND sexually active in last 12 months
primary_infertility = never_gave_birth & sexually_active_12mo

# Combine primary infertility condition
cohort.loc[primary_infertility, 'is_infertile'] = 1

# === SECONDARY INFERTILITY (has children) ===
# 60+ months (5 years) since last birth AND sexually active
secondary_infertility = (
    has_birth &
    valid_v215 &
    (v215 >= 60) &
    sexually_active_12mo
)

cohort.loc[secondary_infertility, 'is_infertile'] = 1

# 3. SELECT FEATURES (The "X")
# Include the new variables we considered
features = [
    'v012',   # current age
    'v445',   # BMI
    'v763a',  # drank alcohol in last 12 months
    'v763c',  # smoked cigarettes in last 12 months
    'v190',   # wealth index
    'v201',   # total children ever born
    'v222',   # months since first cohabitation
    'v511',   # age at first marriage/cohabitation
    'v529'    # months since last sex
]

# Only keep rows with valid data for key variables
cohort_clean = cohort.dropna(subset=['is_infertile'])

X = cohort_clean[features]
y = cohort_clean['is_infertile']

# 4. SAVE CLEANED DATA
cleaned_df = cohort_clean[features + ['is_infertile']]
cleaned_df = cleaned_df.rename(
    columns={
        'v012': 'age',
        'v445': 'bmi',
        'v763a': 'alcohol_last_12mo',
        'v763c': 'smoked_last_12mo',
        'v190': 'wealth_index',
        'v201': 'children_ever_born',
        'v222': 'months_since_first_cohabitation',
        'v511': 'age_at_first_marriage',
        'v529': 'months_since_last_sex',
        'is_infertile': 'infertile',
    }
)
script_dir = Path(__file__).resolve().parent
output_dir = script_dir / "processed"
output_dir.mkdir(parents=True, exist_ok=True)
cleaned_df.to_csv(output_dir / "dhs_cleaned.csv", index=False)

# 5. PRINT SUMMARY STATISTICS
print("=" * 60)
print("Data Cleaning Summary")
print("=" * 60)
print(f"Saved to: {output_dir / 'dhs_cleaned.csv'}")
print(f"Total records: {len(cleaned_df):,}")
print(f"Infertile cases: {y.sum():,} ({y.mean()*100:.2f}%)")
print(f"Fertile cases: {(y==0).sum():,} ({(1-y.mean())*100:.2f}%)")
print()
print("Breakdown by Infertility Type:")
primary_count = ((cleaned_df['children_ever_born'] == 0) & (cleaned_df['infertile'] == 1)).sum()
secondary_count = ((cleaned_df['children_ever_born'] > 0) & (cleaned_df['infertile'] == 1)).sum()
print(f"  - Primary infertility (no children): {primary_count:,}")
print(f"  - Secondary infertility (has children): {secondary_count:,}")
print()
print("Age Distribution of Infertile Cases:")
if y.sum() > 0:
    infertile_ages = cleaned_df[cleaned_df['infertile'] == 1]['age']
    print(f"  - Mean age: {infertile_ages.mean():.1f} years")
    print(f"  - Age range: {infertile_ages.min():.0f} - {infertile_ages.max():.0f} years")
