# ===============================
# Google Form Analysis with Python (Graphs only)
# ===============================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Paths
csv_path = "C:/Users/Kalisa Shadrack/Downloads/Form Responses 1.csv"

# Load data
df = pd.read_csv(csv_path)

# Normalize column names for easy reference
cols = {c.strip(): c for c in df.columns}
def col_like(keywords):
    keyset = [k.lower() for k in keywords]
    for c in df.columns:
        lc = c.lower()
        if all(k in lc for k in keyset):
            return c
    return None

timestamp_col = col_like(["timestamp"])
name_col = col_like(["full","name"])
program_col = col_like(["programme"])
year_col = col_like(["year"])
email_col = col_like(["email"])
contact_col = col_like(["contact"])
have_acct_col = col_like(["bank","account"])   # "Do you have a bank account"
want_ecobank_col = col_like(["open","ecobank"]) # "Would you want to open an account with Ecobank?"
cards_col = None
for c in df.columns:
    if "card" in c.lower():
        cards_col = c
        break

# Clean basic fields
df_year = df[year_col].astype(str).str.strip()
df_program = df[program_col].astype(str).str.strip()

# --- Summary stats ---
total_responses = len(df)
bank_account_counts = df[have_acct_col].astype(str).str.strip().replace({"nan": np.nan}).value_counts(dropna=False)
ecobank_willing_counts = df[want_ecobank_col].astype(str).str.strip().replace({"nan": np.nan}).value_counts(dropna=False)
year_counts = df_year.value_counts(dropna=False)
program_counts = df_program.value_counts(dropna=False)

# Parse card preferences (multi-select, comma-separated)
card_series = pd.Series(dtype=str)
if cards_col is not None:
    exploded = (
        df[cards_col]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )
    exploded = exploded[exploded != ""]
    card_series = exploded
card_pref_counts = card_series.value_counts()

# Cross-tabulations
crosstab_acct_vs_willing = pd.crosstab(
    df[have_acct_col].astype(str).str.strip().replace({"nan": "No response"}),
    df[want_ecobank_col].astype(str).str.strip().replace({"nan": "No response"}),
    dropna=False
)

crosstab_year_vs_willing = pd.crosstab(
    df_year.replace({"nan": "No response"}),
    df[want_ecobank_col].astype(str).str.strip().replace({"nan": "No response"}),
    dropna=False
)

# --- Visualization helpers (direct show) ---
def show_bar(series, title, xlabel, ylabel, top=None, rotate=0):
    s = series.copy()
    if top is not None and len(s) > top:
        top_s = s.head(top)
        other_sum = s.iloc[top:].sum()
        s = pd.concat([top_s, pd.Series({"Other": other_sum})])
    plt.figure()
    s.plot(kind="bar", rot=rotate)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()

def show_pie(series, title):
    plt.figure()
    series.plot(kind="pie", autopct="%1.1f%%")
    plt.title(title)
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

def show_grouped_bar(df_counts, title, xlabel, ylabel, rotate=0):
    plt.figure()
    df_counts.plot(kind="bar", rot=rotate)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()

# --- Generate charts ---
if bank_account_counts.sum() > 0:
    show_pie(bank_account_counts, "Do you have a bank account?")

show_bar(ecobank_willing_counts, "Willingness to Open an Account with Ecobank", 
         "Response", "Count")

show_bar(year_counts, "Year Distribution", "Year", "Count")

show_bar(program_counts, "Programme of Study (Top 10)", "Programme", "Count", 
         top=10, rotate=45)

if not card_pref_counts.empty:
    show_bar(card_pref_counts, "Preferred Card Types", "Card", "Selections", rotate=15)

if not crosstab_acct_vs_willing.empty:
    show_grouped_bar(crosstab_acct_vs_willing, "Have Bank Account vs Want to Open Ecobank", 
                     "Have Bank Account", "Count")

if not crosstab_year_vs_willing.empty:
    show_grouped_bar(crosstab_year_vs_willing, "Year vs Willingness to Open Ecobank", 
                     "Year", "Count")
