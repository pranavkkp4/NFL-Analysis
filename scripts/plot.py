import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# PATHS (match your structure)
# =============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

YEARS_2015_2020 = list(range(2015, 2021))
YEARS_2020_2025 = list(range(2020, 2026))  # overlap intentional

# =============================
# LOADERS
# =============================
def load_passing_year(year: int) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{year} passing.csv")
    df = pd.read_csv(path)
    df = df[df["Player"].astype(str).str.lower() != "league average"].copy()
    df["Season"] = year
    df["QBR"] = pd.to_numeric(df["QBR"], errors="coerce")
    return df.dropna(subset=["QBR"])

def load_rushing_year(year: int) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{year} rushing.csv")

    # Try header=0; fallback to header=1 (PFR quirk)
    try:
        df = pd.read_csv(path)
        if "Player" not in df.columns:
            raise ValueError("Missing Player column")
    except Exception:
        df = pd.read_csv(path, header=1)

    df = df[df["Player"].astype(str).str.lower() != "league average"].copy()
    df["Season"] = year

    for col in ["Succ%", "Y/A", "Yds", "TD"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Succ%", "Y/A", "Yds", "TD"])

# =============================
# METRICS
# =============================
def compute_rbr(df: pd.DataFrame) -> pd.DataFrame:
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
# PLOTTING (VERTICAL BARS + NAMES INSIDE BARS)
# =============================
def plot_grouped_top5_by_year(df: pd.DataFrame, value_col: str, title: str, out_file: str):
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

    # Slightly more headroom so labels don’t clip
    ymax = top[value_col].max()
    plt.ylim(0, ymax * 1.12)

    for rank in range(5):
        slice_r = top.groupby("Season").nth(rank).reset_index()
        offsets = x + (rank - 2) * bar_width

        bars = plt.bar(offsets, slice_r[value_col], width=bar_width)

        # Put LAST NAME INSIDE BAR near top
        for b, name in zip(bars, slice_r["Player"].astype(str)):
            last = name.split(" ")[-1]
            height = b.get_height()

            # Place text inside bar (a little below the top)
            y_text = height * 0.94  # inside the bar
            plt.text(
                b.get_x() + b.get_width()/2,
                y_text,
                last,
                ha="center",
                va="top",
                fontsize=9,
                fontweight="bold",
                color="white",
                rotation=90,   # keeps it readable even in narrow bars
                clip_on=True
            )

    plt.xticks(x, seasons)
    plt.ylabel(value_col)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_file, dpi=220)
    plt.close()

def main():
    qb_all = pd.concat([load_passing_year(y) for y in range(2015, 2026)], ignore_index=True)
    rb_all = pd.concat([load_rushing_year(y) for y in range(2015, 2026)], ignore_index=True)
    rb_all = compute_rbr(rb_all)

    # QB grouped charts
    plot_grouped_top5_by_year(
        qb_all[qb_all["Season"].isin(YEARS_2015_2020)],
        "QBR",
        "Top 5 Quarterbacks by QBR (2015–2020)",
        os.path.join(FIG_DIR, "top5_qb_2015_2020.png")
    )
    plot_grouped_top5_by_year(
        qb_all[qb_all["Season"].isin(YEARS_2020_2025)],
        "QBR",
        "Top 5 Quarterbacks by QBR (2020–2025)",
        os.path.join(FIG_DIR, "top5_qb_2020_2025.png")
    )

    # RB grouped charts
    plot_grouped_top5_by_year(
        rb_all[rb_all["Season"].isin(YEARS_2015_2020)],
        "RBR",
        "Top 5 Running Backs by RBR (2015–2020)",
        os.path.join(FIG_DIR, "top5_rb_2015_2020.png")
    )
    plot_grouped_top5_by_year(
        rb_all[rb_all["Season"].isin(YEARS_2020_2025)],
        "RBR",
        "Top 5 Running Backs by RBR (2020–2025)",
        os.path.join(FIG_DIR, "top5_rb_2020_2025.png")
    )

    print("Done: regenerated grouped charts with labels inside bars.")

if __name__ == "__main__":
    main()
