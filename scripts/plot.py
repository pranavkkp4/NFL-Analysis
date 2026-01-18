"""
plot.py

End-to-end plotting script for NFL Analysis site.

Expected repo structure (based on your screenshot):
NFL-Analysis/
  raw_data/
    2015 passing.csv
    2015 rushing.csv
    ...
    NFL Salary by Position group.csv
  figures/
  scripts/
    plot.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# PATH HANDLING (MATCHES YOUR STRUCTURE)
# =============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RAW_DIR = os.path.join(BASE_DIR, "raw_data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# =============================
# YEAR GROUPS
# =============================
YEARS_2015_2020 = list(range(2015, 2021))
YEARS_2020_2025 = list(range(2020, 2026))  # overlap intentional per your earlier spec

# =============================
# LOADERS
# =============================
def load_passing_year(year: int) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{year} passing.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing passing file: {path}")

    df = pd.read_csv(path)
    df = df[df["Player"].astype(str).str.lower() != "league average"]
    df["Season"] = year

    # Ensure QBR numeric
    df["QBR"] = pd.to_numeric(df.get("QBR", np.nan), errors="coerce")
    df = df.dropna(subset=["QBR"])

    return df


def load_rushing_year(year: int) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{year} rushing.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing rushing file: {path}")

    # Try normal header first; if it fails, try header=1 (PFR quirk)
    try:
        df = pd.read_csv(path)
        if "Player" not in df.columns:
            raise ValueError("Missing Player column")
    except Exception:
        df = pd.read_csv(path, header=1)

    df = df[df["Player"].astype(str).str.lower() != "league average"]
    df["Season"] = year

    # Required columns for RBR
    for col in ["Succ%", "Y/A", "Yds", "TD"]:
        if col not in df.columns:
            raise ValueError(f"Rushing file {path} missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Succ%", "Y/A", "Yds", "TD"])
    return df

# =============================
# METRICS
# =============================
def compute_rbr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Running Back Rating (RBR):
    Equal-weighted z-score (per season) of:
      - Success Rate (Succ%)
      - Yards per Attempt (Y/A)
      - Total Yards (Yds)
      - Total Touchdowns (TD)
    """

    def zscore(s):
        return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

    out = df.copy()
    out["z_succ"] = out.groupby("Season")["Succ%"].transform(zscore)
    out["z_ypa"]  = out.groupby("Season")["Y/A"].transform(zscore)
    out["z_yds"]  = out.groupby("Season")["Yds"].transform(zscore)
    out["z_td"]   = out.groupby("Season")["TD"].transform(zscore)

    out["RBR"] = (out["z_succ"] + out["z_ypa"] + out["z_yds"] + out["z_td"]) / 4.0
    return out

# =============================
# PLOTTING (VERTICAL BARS)
# =============================
def plot_top5_by_year(df: pd.DataFrame, value_col: str, title: str, out_file: str):
    """
    Grouped VERTICAL bar chart:
      - X-axis: seasons
      - 5 bars per season (Top 5 players)
    """
    seasons = sorted(df["Season"].unique())

    top = (
        df.sort_values(["Season", value_col], ascending=[True, False])
          .groupby("Season")
          .head(5)
          .reset_index(drop=True)
    )

    bar_width = 0.14
    x = np.arange(len(seasons))

    plt.figure(figsize=(18, 6))

    for rank in range(5):
        slice_r = top.groupby("Season").nth(rank).reset_index()
        offsets = x + (rank - 2) * bar_width

        # VERTICAL bars (this guarantees vertical orientation)
        plt.bar(offsets, slice_r[value_col], width=bar_width)

        # annotate with last names
        for ox, val, name in zip(offsets, slice_r[value_col], slice_r["Player"]):
            last = str(name).split(" ")[-1]
            plt.text(
                ox, val, last,
                rotation=90, fontsize=7,
                ha="center", va="bottom"
            )

    plt.xticks(x, seasons)
    plt.ylabel(value_col)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_file, dpi=200)
    plt.close()

# =============================
# MAIN
# =============================
def main():
    # Load all seasons (expects all 2015–2025 raw CSVs to exist)
    qb_all = pd.concat([load_passing_year(y) for y in range(2015, 2026)], ignore_index=True)
    rb_all = pd.concat([load_rushing_year(y) for y in range(2015, 2026)], ignore_index=True)
    rb_all = compute_rbr(rb_all)

    # QB grouped charts
    plot_top5_by_year(
        qb_all[qb_all["Season"].isin(YEARS_2015_2020)],
        "QBR",
        "Top 5 Quarterbacks by QBR (2015–2020)",
        os.path.join(FIG_DIR, "top5_qb_2015_2020.png")
    )

    plot_top5_by_year(
        qb_all[qb_all["Season"].isin(YEARS_2020_2025)],
        "QBR",
        "Top 5 Quarterbacks by QBR (2020–2025)",
        os.path.join(FIG_DIR, "top5_qb_2020_2025.png")
    )

    # RB grouped charts
    plot_top5_by_year(
        rb_all[rb_all["Season"].isin(YEARS_2015_2020)],
        "RBR",
        "Top 5 Running Backs by RBR (2015–2020)",
        os.path.join(FIG_DIR, "top5_rb_2015_2020.png")
    )

    plot_top5_by_year(
        rb_all[rb_all["Season"].isin(YEARS_2020_2025)],
        "RBR",
        "Top 5 Running Backs by RBR (2020–2025)",
        os.path.join(FIG_DIR, "top5_rb_2020_2025.png")
    )

    print("All plots generated successfully.")
    print("Saved to:", FIG_DIR)

if __name__ == "__main__":
    main()
