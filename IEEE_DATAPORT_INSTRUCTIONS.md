# IEEE Dataport — Instructions Field (copy-paste this)

---

## Dataset Overview

This dataset contains **5,884,387 Bitcoin transactions** (blocks 744,837–903,456, July 2022 – July 2025) with **53 structural, temporal, and heuristic features** per transaction, including a binary label (`is_coinjoin_like`) identifying CoinJoin-like mixing activity. It was collected and labelled to support research on Bitcoin privacy, CoinJoin deanonymization, and ML-based illicit-transaction detection.

---

## Files Included

| File | Description |
|------|-------------|
| `Dataset.parquet` | Main dataset — 5.88M transactions, 53 columns, Snappy-compressed Parquet |
| `DATASET_DOCUMENTATION.md` | Full data dictionary with column descriptions and labelling methodology |
| `dataset_visualization.png` | 10-panel descriptive overview figure |

---

## Requirements

- Python 3.8+
- `pandas >= 1.5`, `pyarrow >= 10` (to read Parquet)
- Optional: `matplotlib`, `scikit-learn`, `numpy`

Install with:

```
pip install pandas pyarrow matplotlib scikit-learn numpy
```

---

## How to Load the Dataset

```python
import pandas as pd

df = pd.read_parquet("Dataset.parquet")
print(df.shape)          # (5884387, 53)
print(df.dtypes)
print(df["is_coinjoin_like"].value_counts())
```

---

## Splitting into Train / Test Sets

```python
from sklearn.model_selection import train_test_split

X = df.drop(columns=["txid", "is_coinjoin_like", "input_addresses",
                      "output_addresses", "input_script_types",
                      "output_script_types", "op_return_data",
                      "timestamp", "month_1", "block_time"])
y = df["is_coinjoin_like"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

---

## Handling Class Imbalance

The dataset is imbalanced (1.88% CoinJoin-like). Recommended strategies:

**Option 1 — Class weights (Random Forest / XGBoost)**
```python
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(class_weight="balanced", n_estimators=100)
clf.fit(X_train, y_train)
```

**Option 2 — SMOTE oversampling**
```python
from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)
```

**Option 3 — ADASYN (recommended for graph-based methods)**
```python
from imblearn.over_sampling import ADASYN
ada = ADASYN(random_state=42)
X_res, y_res = ada.fit_resample(X_train, y_train)
```

---

## Recommended Evaluation Metrics

Because of class imbalance, accuracy alone is misleading. Use:

- **Precision, Recall, F1-score** on the minority (CoinJoin-like) class
- **PR-AUC** (Precision-Recall Area Under Curve) — preferred over ROC-AUC for imbalanced datasets
- **Confusion matrix** for threshold analysis

```python
from sklearn.metrics import classification_report, average_precision_score

y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred, target_names=["Normal", "CoinJoin-like"]))
print("PR-AUC:", average_precision_score(y_test, y_prob))
```

---

## Key Feature Groups

| Group | Columns |
|-------|---------|
| Transaction structure | `input_count`, `output_count`, `size`, `vsize`, `weight` |
| Value & fees | `total_input_value`, `fee`, `fee_rate_sat_per_vbyte`, `avg_output_value`, `value_concentration_ratio` |
| Address analysis | `input_address_count`, `output_address_count`, `address_reuse` |
| Script types | `has_p2pkh`, `has_p2sh`, `has_p2wpkh`, `has_p2wsh`, `has_taproot` |
| Temporal | `hour`, `day_of_week`, `week_of_year`, `year` |
| Heuristic flags | `is_consolidation`, `is_distribution`, `is_peer_to_peer`, `is_batch_payment`, `rbf_enabled` |
| **Label** | **`is_coinjoin_like`** |

---

## Labelling Methodology

A transaction is labelled `is_coinjoin_like = True` when it satisfies all of:
1. `input_address_count >= 2` (multiple distinct spending parties)
2. At least two outputs share an equal BTC value (standardised denomination)
3. `output_count >= 2`
4. `has_coinbase = False`

This follows established heuristics from the CoinJoin detection literature.

---

## Dataset Access

- IEEE Dataport DOI: 10.21227/bxmt-mn56
- GitHub Mirror: https://github.com/sagarkorde/ParquetDataset

---

## Citation

If you use this dataset, please cite:

> Korde, S., Shekokar, N., & Siddavatam, I. (2026). Bitcoin Blockchain Transaction Dataset for Wallet Address Profiling and Behavioral Analysis (Parquet Format). IEEE Dataport. DOI: 10.21227/bxmt-mn56

Associated paper:

> Korde, S. et al. (2026). HyGAP: A Multi-Layered Hybrid Framework for Behavioral Bitcoin Wallet Profiling and Unsupervised Anomaly Detection. ICCUBEA 2026, Paper ID 1504.

---

## Contact

**sagarkorde04@gmail.com**
