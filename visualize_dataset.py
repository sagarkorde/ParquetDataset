"""
Visualization script for the MixTrace CoinJoin Author Dataset.
Generates a multi-panel figure suitable for IEEE Dataport submission.
Output: dataset_visualization.png  (~2-8 MB, well under 100 MB)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from collections import Counter

# ── Colour palette ────────────────────────────────────────────────────────────
C_CJ   = "#E63946"   # CoinJoin-like  – red
C_NON  = "#457B9D"   # Normal tx      – steel blue
C_PALE = "#A8DADC"   # accent
GREY   = "#6B6B6B"

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading dataset …")
df = pd.read_parquet("Dataset.parquet")
print(f"  {len(df):,} rows × {df.shape[1]} columns")

# Convenience masks
cj  = df["is_coinjoin_like"]
n_total = len(df)
n_cj    = cj.sum()
n_non   = n_total - n_cj

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 24), facecolor="white")
fig.suptitle(
    "MixTrace CoinJoin Author Dataset — Descriptive Overview",
    fontsize=18, fontweight="bold", y=0.995, color="#1D3557"
)

gs = gridspec.GridSpec(
    4, 3,
    figure=fig,
    hspace=0.52, wspace=0.35,
    top=0.970, bottom=0.04, left=0.07, right=0.97
)

ax = {
    "class"    : fig.add_subplot(gs[0, 0]),
    "monthly"  : fig.add_subplot(gs[0, 1:]),
    "txtype"   : fig.add_subplot(gs[1, :2]),
    "script"   : fig.add_subplot(gs[1, 2]),
    "fee"      : fig.add_subplot(gs[2, 0]),
    "io_cnt"   : fig.add_subplot(gs[2, 1]),
    "hour"     : fig.add_subplot(gs[2, 2]),
    "weight"   : fig.add_subplot(gs[3, 0]),
    "vcr"      : fig.add_subplot(gs[3, 1]),
    "stats"    : fig.add_subplot(gs[3, 2]),
}

# ── Helper ────────────────────────────────────────────────────────────────────
def subtitle(a, txt):
    a.set_title(txt, fontsize=11, fontweight="bold", color="#1D3557", pad=6)

# ══════════════════════════════════════════════════════════════════════════════
# 1. Class distribution  (donut)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["class"]
sizes  = [n_non, n_cj]
labels = [f"Normal\n{n_non/n_total*100:.1f}%", f"CoinJoin-like\n{n_cj/n_total*100:.1f}%"]
colors = [C_NON, C_CJ]
wedges, _ = a.pie(
    sizes, labels=None, colors=colors,
    startangle=90, wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2)
)
a.text(0, 0, f"{n_total/1e6:.2f}M\ntxns", ha="center", va="center",
       fontsize=12, fontweight="bold", color="#1D3557")
legend_els = [Patch(color=C_NON, label=f"Normal  ({n_non:,})"),
              Patch(color=C_CJ,  label=f"CoinJoin-like  ({n_cj:,})")]
a.legend(handles=legend_els, loc="lower center", bbox_to_anchor=(0.5, -0.18),
         fontsize=8, frameon=False)
subtitle(a, "Class Distribution")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Monthly transaction volume
# ══════════════════════════════════════════════════════════════════════════════
a = ax["monthly"]
monthly_all = df.groupby("month_1").size().rename("all")
monthly_cj  = df[cj].groupby(df.loc[cj, "month_1"]).size().rename("cj")
monthly     = pd.concat([monthly_all, monthly_cj], axis=1).sort_index()
monthly["non"] = monthly["all"] - monthly["cj"].fillna(0)
monthly = monthly.dropna(subset=["all"])

x = np.arange(len(monthly))
bar_w = 0.72
a.bar(x, monthly["non"] / 1000, bar_w, color=C_NON, label="Normal")
a.bar(x, monthly["cj"].fillna(0) / 1000, bar_w,
      bottom=monthly["non"] / 1000, color=C_CJ, label="CoinJoin-like")
a.set_xticks(x[::3])
a.set_xticklabels(monthly.index[::3], rotation=45, ha="right", fontsize=7)
a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}k"))
a.set_ylabel("Transactions (thousands)", fontsize=9)
a.legend(fontsize=8, loc="upper left", frameon=False)
a.set_xlim(-0.6, len(monthly) - 0.4)
subtitle(a, "Monthly Transaction Volume (2022-2024)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Transaction-type flags  (grouped bar)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["txtype"]
tx_flags = ["is_self_transfer","is_consolidation","is_distribution",
            "is_peer_to_peer","is_batch_payment","rbf_enabled",
            "has_op_return","has_coinbase"]
labels_f = ["Self-Transfer","Consolidation","Distribution",
            "P2P","Batch Payment","RBF","OP_RETURN","Coinbase"]

pct_non = [(~cj & df[f]).sum() / n_non * 100 for f in tx_flags]
pct_cj  = [( cj & df[f]).sum() / n_cj  * 100 for f in tx_flags]

x = np.arange(len(tx_flags))
bw = 0.38
bars_non = a.bar(x - bw/2, pct_non, bw, color=C_NON, label="Normal")
bars_cj  = a.bar(x + bw/2, pct_cj,  bw, color=C_CJ,  label="CoinJoin-like")
a.set_xticks(x)
a.set_xticklabels(labels_f, rotation=30, ha="right", fontsize=8)
a.set_ylabel("% of class", fontsize=9)
a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
a.legend(fontsize=9, frameon=False)
subtitle(a, "Transaction-Type Flag Prevalence by Class")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Script-type prevalence (horizontal bar)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["script"]
script_flags = ["has_p2pk","has_p2pkh","has_p2sh","has_p2wpkh","has_p2wsh","has_taproot"]
script_names = ["P2PK","P2PKH","P2SH","P2WPKH","P2WSH","Taproot"]

pct_s_non = [(~cj & df[f]).sum() / n_non * 100 for f in script_flags]
pct_s_cj  = [( cj & df[f]).sum() / n_cj  * 100 for f in script_flags]

y = np.arange(len(script_flags))
bw = 0.38
a.barh(y + bw/2, pct_s_non, bw, color=C_NON, label="Normal")
a.barh(y - bw/2, pct_s_cj,  bw, color=C_CJ,  label="CoinJoin-like")
a.set_yticks(y)
a.set_yticklabels(script_names, fontsize=8)
a.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
a.set_xlabel("% of class", fontsize=9)
a.legend(fontsize=7, frameon=False)
subtitle(a, "Script Type\nPrevalence")

# ══════════════════════════════════════════════════════════════════════════════
# 5. Fee-rate distribution  (CJ vs Non-CJ)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["fee"]
fr_non = df.loc[~cj, "fee_rate_sat_per_vbyte"].dropna()
fr_cj  = df.loc[ cj, "fee_rate_sat_per_vbyte"].dropna()

# Cap at 99th pct for readability
cap = max(fr_non.quantile(0.99), fr_cj.quantile(0.99))
bins = np.linspace(0, cap, 60)
a.hist(fr_non, bins=bins, density=True, color=C_NON, alpha=0.7, label="Normal")
a.hist(fr_cj,  bins=bins, density=True, color=C_CJ,  alpha=0.7, label="CoinJoin-like")
a.set_xlabel("Fee rate (sat/vByte)", fontsize=9)
a.set_ylabel("Density", fontsize=9)
a.legend(fontsize=8, frameon=False)
subtitle(a, "Fee Rate Distribution")

# ══════════════════════════════════════════════════════════════════════════════
# 6. Input & output count scatter (log-scale violin proxy)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["io_cnt"]
# Sample to keep it fast
rng = np.random.default_rng(42)
idx_non = rng.choice(np.where(~cj)[0], size=min(40_000, n_non), replace=False)
idx_cj  = rng.choice(np.where( cj)[0], size=min(40_000, n_cj),  replace=False)

data_parts = [
    (df.iloc[idx_non]["input_count"],  df.iloc[idx_non]["output_count"],  C_NON, "Normal",        0.10),
    (df.iloc[idx_cj ]["input_count"],  df.iloc[idx_cj ]["output_count"],  C_CJ,  "CoinJoin-like", 0.05),
]
for ic, oc, col, lbl, alp in data_parts:
    a.scatter(ic.clip(upper=100), oc.clip(upper=100),
              s=1, alpha=alp, color=col, label=lbl, rasterized=True)

a.set_xlabel("Input count (capped at 100)", fontsize=9)
a.set_ylabel("Output count (capped at 100)", fontsize=9)
legend_els2 = [Patch(color=C_NON, label="Normal"),
               Patch(color=C_CJ,  label="CoinJoin-like")]
a.legend(handles=legend_els2, fontsize=8, frameon=False)
subtitle(a, "Input vs Output Count")

# ══════════════════════════════════════════════════════════════════════════════
# 7. Hour-of-day activity heatmap (day-of-week × hour)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["hour"]
pivot = df[cj].groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)
pivot = pivot.reindex(index=range(7), columns=range(24), fill_value=0)
im = a.imshow(pivot.values, aspect="auto", cmap="YlOrRd", interpolation="nearest")
a.set_xticks(range(0, 24, 4))
a.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 4)], fontsize=7)
a.set_yticks(range(7))
a.set_yticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], fontsize=7)
plt.colorbar(im, ax=a, shrink=0.85, label="CoinJoin tx count")
subtitle(a, "CoinJoin Activity\n(Day × Hour, UTC)")

# ══════════════════════════════════════════════════════════════════════════════
# 8. Transaction weight distribution
# ══════════════════════════════════════════════════════════════════════════════
a = ax["weight"]
w_non = df.loc[~cj, "weight"].dropna()
w_cj  = df.loc[ cj, "weight"].dropna()
cap_w = min(w_non.quantile(0.99), w_cj.quantile(0.99), 400_000)
bins_w = np.linspace(0, cap_w, 60)
a.hist(w_non, bins=bins_w, density=True, color=C_NON, alpha=0.7, label="Normal")
a.hist(w_cj,  bins=bins_w, density=True, color=C_CJ,  alpha=0.7, label="CoinJoin-like")
a.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
a.set_xlabel("Weight (WU)", fontsize=9)
a.set_ylabel("Density", fontsize=9)
a.legend(fontsize=8, frameon=False)
subtitle(a, "Transaction Weight Distribution")

# ══════════════════════════════════════════════════════════════════════════════
# 9. Value concentration ratio  (CDF)
# ══════════════════════════════════════════════════════════════════════════════
a = ax["vcr"]
for mask, col, lbl in [(~cj, C_NON, "Normal"), (cj, C_CJ, "CoinJoin-like")]:
    v = df.loc[mask, "value_concentration_ratio"].dropna().sort_values()
    cdf = np.linspace(0, 1, len(v))
    a.plot(v, cdf, color=col, lw=1.4, label=lbl)
a.set_xlabel("Value Concentration Ratio", fontsize=9)
a.set_ylabel("CDF", fontsize=9)
a.legend(fontsize=8, frameon=False)
subtitle(a, "Value Concentration Ratio (CDF)")

# ══════════════════════════════════════════════════════════════════════════════
# 10. Dataset statistics table
# ══════════════════════════════════════════════════════════════════════════════
a = ax["stats"]
a.axis("off")
rows = [
    ("Total transactions",        f"{n_total:,}"),
    ("CoinJoin-like",             f"{n_cj:,}  ({n_cj/n_total*100:.1f}%)"),
    ("Normal",                    f"{n_non:,}  ({n_non/n_total*100:.1f}%)"),
    ("Features",                  f"{df.shape[1]}"),
    ("Date range",                f"{df['timestamp'].min().date()} –\n{df['timestamp'].max().date()}"),
    ("Blocks covered",            f"{df['block_height'].min():,} – {df['block_height'].max():,}"),
    ("Median fee (sat/vB)",       f"{df['fee_rate_sat_per_vbyte'].median():.1f}"),
    ("Median input count",        f"{df['input_count'].median():.0f}"),
    ("Median output count",       f"{df['output_count'].median():.0f}"),
    ("Taproot tx share",          f"{df['has_taproot'].mean()*100:.1f}%"),
    ("Unique months",             f"{df['month_1'].nunique()}"),
]
col_labels = ["Statistic", "Value"]
table = a.table(
    cellText=rows, colLabels=col_labels,
    loc="center", cellLoc="left"
)
table.auto_set_font_size(False)
table.set_fontsize(8.5)
table.scale(1, 1.55)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#1D3557")
        cell.set_text_props(color="white", fontweight="bold")
    elif r % 2 == 0:
        cell.set_facecolor("#F0F4F8")
    else:
        cell.set_facecolor("white")
subtitle(a, "Dataset Summary Statistics")

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = "dataset_visualization.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved -> {out_path}")

import os
size_mb = os.path.getsize(out_path) / 1e6
print(f"File size: {size_mb:.2f} MB")
plt.close(fig)
