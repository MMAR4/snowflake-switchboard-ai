# Snowflake Switchboard AI (`snowflake-switchboard-ai`)

[![PyPI version](https://badge.fury.io/py/snowflake-switchboard-ai.svg)](https://pypi.org/project/snowflake-switchboard-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

`snowflake-switchboard-ai` is a metadata-driven, zero-cost query router for **Snowflake** and **Snowpark**.

It automatically inspects your query execution plan before execution to estimate projected data volumes (`bytesAssigned`), dynamically routing your queries to the optimal warehouse tier to maximize performance while minimizing compute costs.



## 🚀 Key Features

* **Zero-Cost Telemetry Analysis:** Uses Snowflake's native `SYSTEM$EXPLAIN_PLAN_JSON` to inspect query payloads without executing them or incurring compute charges.
* **Intelligent Tier Routing:** Automatically maps query byte sizes to your configured warehouse hierarchy.
* **Frictionless Execution:** Provides a clean callable shorthand syntax (`sb(...)`) that analyzes, routes, executes, and renders results automatically.
* **Flexible Configuration:** Works out of the box with sensible size defaults or accepts custom data thresholds tailored to your workload.



## 📦 Step-by-Step Guide

### Step 1: Installation

Install the package directly from [PyPI](https://pypi.org/project/snowflake-switchboard-ai/):

```bash
pip install snowflake-switchboard-ai
```

### Step 2: Quick Start (Default Thresholds)

Simply pass your existing Snowpark session and an ordered warehouse list (from smallest to largest). The switchboard automatically applies smart data size thresholds out of the box:

```python
from switchboard import MultiTierSwitchboard

# 1. Initialize with your active Snowpark session and warehouse hierarchy
# Replace warehouse names with your actual Snowflake warehouse names (ordered XS -> XXL)
sb = MultiTierSwitchboard(
    session=session,
    warehouses=[
        "XSMALL_WH",   # Tier 1 (Default for payloads < 1 GB)
        "SMALL_WH",    # Tier 2 (Payloads < 5 GB)
        "MEDIUM_WH",   # Tier 3 (Payloads < 20 GB)
        "LARGE_WH",    # Tier 4 (Payloads < 50 GB)
        "XLARGE_WH",   # Tier 5 (Payloads < 100 GB)
        "XXLARGE_WH"   # Tier 6 (Fallback for payloads >= 100 GB)
    ]
)

# 2. Run queries effortlessly using the callable shorthand
# Switchboard analyzes the query, switches to the optimal warehouse, and runs the query
sb("""
    SELECT c_mktsegment, COUNT(*) 
    FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER 
    GROUP BY c_mktsegment
""")
```



## 📊 Default Threshold Mapping

When custom thresholds are not specified, `MultiTierSwitchboard` routes queries using these default payload boundaries:

| Warehouse Tier | Byte Boundary | Data Volume Limit |
| :--- | :--- | :--- |
| **Tier 1** (e.g., XS) | `< 1,000,000,000` bytes | Under 1 GB |
| **Tier 2** (e.g., Small) | `< 5,000,000,000` bytes | Under 5 GB |
| **Tier 3** (e.g., Medium) | `< 20,000,000,000` bytes | Under 20 GB |
| **Tier 4** (e.g., Large) | `< 50,000,000,000` bytes | Under 50 GB |
| **Tier 5** (e.g., X-Large) | `< 100,000,000,000` bytes | Under 100 GB |
| **Tier 6** (e.g., 2X-Large) | `< 500,000,000,000` bytes | Under 500 GB |

---

## Step 3: Custom Thresholds (Optional)

If you want granular control over when queries switch warehouse tiers, pass custom byte limits via the `thresholds` parameter:

```python
# Pass custom byte limits matching your warehouse boundaries (in bytes):
sb = MultiTierSwitchboard(
    session=session,
    warehouses=["XSMALL_WH", "SMALL_WH", "MEDIUM_WH"], # List of warehouses in ascending order
    thresholds=[1_000_000_000, 10_000_000_000]          # 1 GB boundary for Small, 10 GB boundary for Medium
)
```



## ⚙️ How It Works

1. **Pre-Check Phase:** Intercepts query execution and executes `SYSTEM$EXPLAIN_PLAN_JSON(...)` at zero compute cost.
2. **Telemetry Analysis:** Recursively parses the JSON plan tree to calculate estimated `bytesAssigned`.
3. **Dynamic Routing:** Automatically executes a fast `USE WAREHOUSE <optimal_tier>` before triggering data retrieval.



## 🛠️ Requirements

* **Python:** `3.8+`
* **Snowpark:** `snowflake-snowpark-python >= 1.0.0`
* **PyPI Package:** [`snowflake-switchboard-ai`](https://pypi.org/project/snowflake-switchboard-ai/)



## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
