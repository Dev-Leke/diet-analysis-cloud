"""
data_analysis.py
Task 1: Nutritional analysis of All_Diets.csv

Outputs (charts + cleaned data) are written to an ./output folder so they can
be captured by a Docker volume mount and persisted to the host machine.

Run it with:  python data_analysis.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # save charts to files; no display window needed
import matplotlib.pyplot as plt
import seaborn as sns


# ---------------------------------------------------------------------------
# 0. OUTPUT FOLDER
# ---------------------------------------------------------------------------
# All generated files go here. A Docker volume can be mounted onto this folder
# so the outputs land on the host disk instead of vanishing with the container.
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
df = pd.read_csv("All_Diets.csv")
print("Loaded dataset:", df.shape[0], "rows,", df.shape[1], "columns\n")


# ---------------------------------------------------------------------------
# 2. CLEAN
# ---------------------------------------------------------------------------
# Normalise text casing so "Paleo" and "paleo" are treated as ONE diet, not two.
df["Diet_type"] = df["Diet_type"].str.strip().str.lower()
df["Cuisine_type"] = df["Cuisine_type"].str.strip().str.lower()

macros = ["Protein(g)", "Carbs(g)", "Fat(g)"]

# Force macro columns to numbers; any stray text becomes NaN (missing).
df[macros] = df[macros].apply(pd.to_numeric, errors="coerce")

# Fill missing macro values with that column's mean (numeric columns only).
df[macros] = df[macros].fillna(df[macros].mean())

print("Missing values after cleaning:\n", df[macros].isna().sum(), "\n")


# ---------------------------------------------------------------------------
# 3. ANALYSES
# ---------------------------------------------------------------------------
# 3a. Average macronutrients per diet type
avg_macros = df.groupby("Diet_type")[macros].mean()
print("=== Average macros per diet type ===")
print(avg_macros.round(2), "\n")

# 3b. Top 5 protein-rich recipes per diet type
top_protein = (df.sort_values("Protein(g)", ascending=False)
                 .groupby("Diet_type")
                 .head(5))
print("=== Top 5 protein recipes per diet type ===")
print(top_protein[["Diet_type", "Recipe_name", "Protein(g)"]]
      .to_string(index=False), "\n")

# 3c. Diet type with the highest protein (by average across its recipes)
highest = avg_macros["Protein(g)"].idxmax()
print(f"=== Highest-protein diet: {highest} "
      f"({avg_macros.loc[highest, 'Protein(g)']:.2f} g avg) ===\n")

# 3d. Most common cuisine per diet type
top_cuisine = (df.groupby("Diet_type")["Cuisine_type"]
                 .agg(lambda s: s.value_counts().idxmax()))
print("=== Most common cuisine per diet type ===")
print(top_cuisine, "\n")

# 3e. New metrics: ratios. .replace(0, np.nan) guards against divide-by-zero.
df["Protein_to_Carbs"] = df["Protein(g)"] / df["Carbs(g)"].replace(0, np.nan)
df["Carbs_to_Fat"] = df["Carbs(g)"] / df["Fat(g)"].replace(0, np.nan)
print("=== Sample of new ratio metrics ===")
print(df[["Recipe_name", "Protein_to_Carbs", "Carbs_to_Fat"]].head().round(2), "\n")

# Save the cleaned + enriched data into the output folder.
df.to_csv(os.path.join(OUTPUT_DIR, "cleaned_diets.csv"), index=False)


# ---------------------------------------------------------------------------
# 4. VISUALISATIONS  (all saved into OUTPUT_DIR)
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid")

# (i) Grouped bar chart: all three macros per diet
avg_macros.plot(kind="bar", figsize=(11, 6))
plt.title("Average macronutrients by diet type")
plt.ylabel("grams")
plt.xlabel("diet type")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "01_avg_macros_bar.png"), dpi=120)
plt.close()

# (ii) Heatmap: diet vs macro intensity
plt.figure(figsize=(8, 6))
sns.heatmap(avg_macros, annot=True, fmt=".1f", cmap="YlGnBu")
plt.title("Macronutrient heatmap by diet type")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "02_macros_heatmap.png"), dpi=120)
plt.close()

# (iii) Scatter: top-5 protein recipes spread across cuisines
plt.figure(figsize=(11, 6))
sns.scatterplot(data=top_protein, x="Cuisine_type", y="Protein(g)",
                hue="Diet_type", s=90)
plt.title("Top 5 protein recipes per diet, by cuisine")
plt.xticks(rotation=45, ha="right")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "03_top_protein_scatter.png"), dpi=120)
plt.close()

print(f"Done. Charts + cleaned_diets.csv saved into ./{OUTPUT_DIR}/")
