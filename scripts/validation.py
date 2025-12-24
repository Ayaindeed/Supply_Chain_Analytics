"""
Validation utilities for data quality checks used across the pipeline.
No external dependencies beyond pandas/numpy.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def validate_raw_dataframe(df: pd.DataFrame) -> None:
    """Validate raw CSV dataframe before loading to PostgreSQL.

    Rules:
    - Required columns exist
    - Primary keys not null: (order_id, order_item_id)
    - Dates parseable: order_date_dateorders, shipping_date_dateorders
    - No duplicate rows on (order_id, order_item_id)
    - Basic numeric sanity: sales >= 0, order_item_total >= 0
    """
    required_cols = [
        "order_id",
        "order_item_id",
        "order_date_dateorders",
        "shipping_date_dateorders",
        "order_customer_id",
        "order_country",
        "sales",
        "order_item_total",
        "order_profit_per_order",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Primary keys not null
    if df["order_id"].isna().any() or df["order_item_id"].isna().any():
        raise ValueError("Null values found in primary key columns (order_id/order_item_id)")

    # Duplicates on composite PK
    dupes = df.duplicated(subset=["order_id", "order_item_id"]).sum()
    if dupes > 0:
        raise ValueError(f"Found {dupes} duplicate rows on (order_id, order_item_id)")

    # Dates parseable
    for date_col in ["order_date_dateorders", "shipping_date_dateorders"]:
        parsed = pd.to_datetime(df[date_col], errors="coerce")
        if parsed.isna().mean() > 0.01:  # >1% unparseable
            raise ValueError(f"Too many unparseable dates in {date_col}")

    # Numerics non-negative (profits may legitimately be negative)
    for num_col in ["sales", "order_item_total"]:
        if (df[num_col] < 0).any():
            raise ValueError(f"Negative values found in numeric column {num_col}")


def validate_features_dataframe(df: pd.DataFrame, required: list[str]) -> None:
    """Validate features dataframe before ML usage.

    - All required columns present
    - No inf/-inf, limited NaNs (< 1%) in required columns
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    # Replace inf with NaN for checks
    df = df.replace([np.inf, -np.inf], np.nan)
    for c in required:
        if df[c].isna().mean() > 0.01:
            raise ValueError(f"Too many NaNs in required feature: {c}")
