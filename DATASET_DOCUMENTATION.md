# MixTrace CoinJoin Author Dataset — Data Dictionary & Documentation

## Overview

This dataset contains **5,884,387 Bitcoin transactions** spanning blocks 744,837 to 903,456 (July 2022 – July 2025), collected and labelled to support research on CoinJoin transaction deanonymization and Bitcoin privacy analysis. Each row represents one on-chain transaction enriched with 53 structural, temporal, and heuristic features, including a binary label (`is_coinjoin_like`) identifying transactions that exhibit CoinJoin-like mixing behaviour.

The dataset was constructed to address three open research gaps in Bitcoin privacy:
1. Taproot-upgrade clustering bypasses (P2TR / Schnorr key indistinguishability)
2. Multi-dimensional post-mix spending (CoinJoin Spending Transaction) deanonymization
3. ML class-imbalance in illicit-activity detection on transaction graphs

---

## File Format

| Property        | Value                            |
|-----------------|----------------------------------|
| File            | `Dataset.parquet`                |
| Format          | Apache Parquet (Snappy-compressed) |
| Rows            | 5,884,387                        |
| Columns         | 53                               |
| Size on disk    | ~550 MB                         |
| Null values     | None (all columns fully populated) |

---

## Class Distribution

| Class              | Count     | Percentage |
|--------------------|-----------|------------|
| Normal             | 5,774,035 | 98.12%     |
| CoinJoin-like      | 110,352   | 1.88%      |
| **Total**          | **5,884,387** | 100%   |

---

## Column Reference (Data Dictionary)

### Identifiers

| Column        | Type    | Description |
|---------------|---------|-------------|
| `txid`        | string  | Unique 256-bit Bitcoin transaction hash (hex-encoded) |
| `block_height`| int32   | Block number in which the transaction was confirmed |
| `block_time`  | int64   | Block timestamp as a Unix epoch integer (seconds since 1970-01-01) |
| `timestamp`   | datetime| Parsed UTC datetime of block confirmation |

### Transaction Structure

| Column              | Type    | Description |
|---------------------|---------|-------------|
| `version`           | int32   | Bitcoin transaction version field (1 or 2) |
| `locktime`          | int32   | Transaction locktime field |
| `size`              | int32   | Raw transaction size in bytes |
| `vsize`             | int32   | Virtual size in vBytes (SegWit weight / 4) |
| `weight`            | int32   | SegWit transaction weight in Weight Units (WU) |
| `input_count`       | int32   | Number of transaction inputs (UTXOs being spent) |
| `output_count`      | int32   | Number of transaction outputs |
| `input_addresses`   | list    | List of input addresses (Bech32 / P2PKH / P2SH strings) |
| `output_addresses`  | list    | List of output addresses |
| `input_script_types`| list    | Script types of each input (semicolon-joined in raw form) |
| `output_script_types`| list   | Script types of each output |
| `op_return_data`    | string  | Raw hex payload of OP_RETURN output (empty string if absent) |

### Value & Fee

| Column                   | Type     | Description |
|--------------------------|----------|-------------|
| `total_input_value`      | float32  | Sum of all input values (BTC) |
| `total_output_value`     | float32  | Sum of all output values (BTC) |
| `fee`                    | float32  | Transaction fee in BTC (`total_input_value - total_output_value`) |
| `avg_input_value`        | float32  | Mean value per input (BTC) |
| `avg_output_value`       | float32  | Mean value per output (BTC) |
| `value_difference`       | float32  | Absolute difference between total input and output value (= fee) |
| `fee_rate_sat_per_byte`  | float32  | Fee in satoshis per raw byte |
| `fee_rate_sat_per_vbyte` | float32  | Fee in satoshis per virtual byte (most relevant for SegWit) |
| `value_concentration_ratio` | float32 | Ratio of maximum output value to total output value; 1.0 = single dominant output |

### Address & Script Counts

| Column                | Type   | Description |
|-----------------------|--------|-------------|
| `input_address_count` | int32  | Number of distinct addresses among inputs |
| `output_address_count`| int32  | Number of distinct addresses among outputs |
| `total_addresses`     | int32  | Total unique addresses across inputs and outputs |
| `input_script_count`  | int32  | Number of input scripts |
| `output_script_count` | int32  | Number of output scripts |
| `address_reuse`       | int32  | Count of addresses that appear in both inputs and outputs |

### Derived Ratios

| Column              | Type    | Description |
|---------------------|---------|-------------|
| `input_output_ratio`| float32 | Ratio of `input_count` to `output_count` |

### Temporal Features

| Column         | Type   | Description |
|----------------|--------|-------------|
| `hour`         | int32  | UTC hour of confirmation (0–23) |
| `day_of_week`  | int32  | Day of the week (0 = Monday … 6 = Sunday) |
| `week_of_year` | int32  | ISO week number (1–53) |
| `year`         | int32  | Year of confirmation |
| `month_1`      | string | Year-month string (e.g. `"2023-08"`) used for monthly aggregation |

### Script-Type Flags (Boolean)

Each flag is `True` if **any** input or output in the transaction uses that script type.

| Column        | Description |
|---------------|-------------|
| `has_p2pk`    | Legacy Pay-to-Public-Key outputs present |
| `has_p2pkh`   | Pay-to-Public-Key-Hash (legacy addresses starting with `1`) |
| `has_p2sh`    | Pay-to-Script-Hash (addresses starting with `3`) |
| `has_p2wpkh`  | Pay-to-Witness-Public-Key-Hash (native SegWit `bc1q` short) |
| `has_p2wsh`   | Pay-to-Witness-Script-Hash (native SegWit `bc1q` long) |
| `has_taproot` | Pay-to-Taproot (Taproot `bc1p` — Schnorr signatures) |

### Transaction-Type Heuristic Flags (Boolean)

Mutually exclusive classification of transaction pattern, derived from input/output structure heuristics.

| Column              | Description |
|---------------------|-------------|
| `has_coinbase`      | Transaction is a coinbase (block reward) transaction |
| `has_op_return`     | At least one output carries an OP_RETURN (data-carrier) payload |
| `rbf_enabled`       | Replace-By-Fee signalling is active (sequence number < 0xFFFFFFFE) |
| `is_self_transfer`  | All input and output addresses are identical (self-send) |
| `is_consolidation`  | Many inputs, few outputs (UTXO consolidation pattern) |
| `is_distribution`   | Few inputs, many outputs (fan-out / distribution pattern) |
| `is_peer_to_peer`   | Single input, two outputs (classic P2P payment with change) |
| `is_batch_payment`  | Single input, many outputs (exchange batch payout pattern) |
| `is_coinjoin_like`  | **Primary label.** Transaction exhibits CoinJoin-like mixing behaviour: multiple equal-value outputs from multiple distinct input addresses |

### Metadata

| Column        | Type   | Description |
|---------------|--------|-------------|
| `sample_size` | int32  | Total number of transactions in the block-range sample from which this row was drawn (used for stratified sampling context) |

---

## Labelling Methodology

A transaction is labelled `is_coinjoin_like = True` if it satisfies all of the following heuristic criteria, derived from the academic literature on CoinJoin detection:

1. **Multiple input addresses** — `input_address_count >= 2`, indicating coordination among distinct wallet holders.
2. **Equal-value outputs** — at least two outputs share the same BTC value (within floating-point tolerance), consistent with standardised denomination mixing.
3. **Non-trivial fan-out** — `output_count >= 2`, excluding simple self-transfers.
4. **No coinbase** — `has_coinbase = False`.

These criteria follow the detection logic described in the MixTrace multi-modal forensic framework (see associated paper).

---

## Coverage

| Property            | Value                    |
|---------------------|--------------------------|
| Start date          | 2022-07-13               |
| End date            | 2025-07-01               |
| Start block         | 744,837                  |
| End block           | 903,456                  |
| Unique months       | 30                       |
| Taproot tx share    | ~41% of dataset          |

---

## Dataset Access

| Resource        | Link |
|-----------------|------|
| IEEE Dataport   | https://ieee-dataport.org/documents/bitcoin-blockchain-transaction-dataset-wallet-address-profiling-and-behavioral-analysis |
| DOI             | 10.21227/bxmt-mn56 |
| GitHub Mirror   | https://github.com/sagarkorde/ParquetDataset |

---

## Suggested Citation

If you use this dataset, please cite:

> Korde, S., Shekokar, N., & Siddavatam, I. (2026). *Bitcoin Blockchain Transaction Dataset for Wallet Address Profiling and Behavioral Analysis (Parquet Format).* IEEE Dataport. DOI: 10.21227/bxmt-mn56

Associated paper:

> Korde, S. et al. (2026). *HyGAP: A Multi-Layered Hybrid Framework for Behavioral Bitcoin Wallet Profiling and Unsupervised Anomaly Detection.* ICCUBEA 2026, Paper ID 1504, Track: Blockchain And Cyber Security.

---

## License

This dataset is released for academic and non-commercial research use. Redistribution with attribution is permitted. Commercial use requires explicit written consent from the authors.

---

## Contact

For questions regarding dataset construction, labelling methodology, or usage:
**sagarkorde04@gmail.com**
