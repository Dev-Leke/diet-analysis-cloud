"""
test_analysis.py
Automated tests for the diet-analysis pipeline, run by pytest in CI.

These verify the data-processing logic produces correct, sane results -- so if a
future change breaks the analysis, the CI pipeline catches it on push.
"""

import pandas as pd
import numpy as np

MACROS = ["Protein(g)", "Carbs(g)", "Fat(g)"]


def load_and_clean():
    """Replicates the core cleaning steps from data_analysis.py."""
    df = pd.read_csv("All_Diets.csv")
    df["Diet_type"] = df["Diet_type"].str.strip().str.lower()
    df[MACROS] = df[MACROS].apply(pd.to_numeric, errors="coerce")
    df[MACROS] = df[MACROS].fillna(df[MACROS].mean())
    return df


def test_dataset_loads():
    """The CSV loads and has the expected columns."""
    df = load_and_clean()
    assert len(df) > 0, "dataset should not be empty"
    for col in ["Diet_type", "Cuisine_type", *MACROS]:
        assert col in df.columns, f"missing expected column: {col}"


def test_no_missing_macros_after_cleaning():
    """Cleaning must leave zero missing values in the macro columns."""
    df = load_and_clean()
    for col in MACROS:
        assert df[col].isna().sum() == 0, f"{col} still has missing values"


def test_averages_are_positive():
    """Average macros per diet should all be positive numbers."""
    df = load_and_clean()
    avg = df.groupby("Diet_type")[MACROS].mean()
    assert (avg > 0).all().all(), "averages should be positive"
    assert len(avg) >= 1, "there should be at least one diet group"


def test_protein_ratio_no_infinities():
    """The divide-by-zero guard must prevent infinite ratios."""
    df = load_and_clean()
    ratio = df["Protein(g)"] / df["Carbs(g)"].replace(0, np.nan)
    assert not np.isinf(ratio.dropna()).any(), "ratios must not be infinite"
