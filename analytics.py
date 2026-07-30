from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "CustomerId", "Surname", "CreditScore", "Geography", "Gender", "Age",
    "Tenure", "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary", "Exited"
}

def load_data(path: str | Path) -> pd.DataFrame:
    """Load and validate the European bank customer dataset."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {path}. "
            "Ensure data/European_Bank.csv is committed to the GitHub repository."
        )

    data = pd.read_csv(path)

    if data.empty:
        raise ValueError("The dataset exists but contains no records.")

    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    return data.drop_duplicates(subset=["CustomerId"]).copy()

def add_features(data: pd.DataFrame) -> pd.DataFrame:
    """Create interpretable engagement, relationship and retention features."""
    out = data.copy()
    out["RetentionStatus"] = np.where(out["Exited"].eq(1), "Churned", "Retained")
    out["ActivityStatus"] = np.where(out["IsActiveMember"].eq(1), "Active", "Inactive")
    out["CardStatus"] = np.where(out["HasCrCard"].eq(1), "Credit Card", "No Credit Card")
    out["AgeBand"] = pd.cut(
        out["Age"],
        bins=[17, 29, 39, 49, 59, 120],
        labels=["18-29", "30-39", "40-49", "50-59", "60+"],
        include_lowest=True,
    ).astype(str)

    high_balance_threshold = out["Balance"].quantile(0.75)
    conditions = [
        out["IsActiveMember"].eq(1) & out["NumOfProducts"].ge(2),
        out["IsActiveMember"].eq(1) & out["NumOfProducts"].eq(1),
        out["IsActiveMember"].eq(0) & out["Balance"].ge(high_balance_threshold),
    ]
    choices = ["Active Engaged", "Active Low-Product", "Inactive High-Balance"]
    out["EngagementSegment"] = np.select(
        conditions, choices, default="Inactive Disengaged"
    )

    product_component = (
        out["NumOfProducts"]
        .map({1: 0.45, 2: 1.0, 3: 0.35, 4: 0.15})
        .fillna(0.15)
    )
    balance_rank = out["Balance"].rank(pct=True)
    out["RelationshipStrengthIndex"] = (
        out["IsActiveMember"] * 35
        + product_component * 30
        + (out["Tenure"].clip(0, 10) / 10) * 15
        + out["HasCrCard"] * 5
        + balance_rank * 15
    ).round(1)
    out["RelationshipTier"] = pd.cut(
        out["RelationshipStrengthIndex"],
        bins=[-np.inf, 40, 60, 75, np.inf],
        labels=["Weak", "Developing", "Strong", "Very Strong"],
    ).astype(str)
    return out

def calculate_kpis(data: pd.DataFrame) -> dict[str, float]:
    """Calculate dashboard KPIs from the currently filtered data."""
    if data.empty:
        return {
            "customers": 0, "churn_rate": 0.0, "retention_rate": 0.0,
            "active_rate": 0.0, "engagement_retention_ratio": 0.0,
            "avg_products": 0.0, "product_depth_index": 0.0,
            "high_balance_disengagement_rate": 0.0,
            "credit_card_stickiness_score": 0.0,
            "relationship_strength_index": 0.0,
        }

    active = data[data["IsActiveMember"].eq(1)]
    cardholders = data[data["HasCrCard"].eq(1)]
    q75 = data["Balance"].quantile(0.75)
    high_balance = data[data["Balance"].ge(q75)]

    return {
        "customers": int(len(data)),
        "churn_rate": float(data["Exited"].mean()),
        "retention_rate": float(1 - data["Exited"].mean()),
        "active_rate": float(data["IsActiveMember"].mean()),
        "engagement_retention_ratio": (
            float(1 - active["Exited"].mean()) if not active.empty else 0.0
        ),
        "avg_products": float(data["NumOfProducts"].mean()),
        "product_depth_index": float(
            data["NumOfProducts"].mean() / max(data["NumOfProducts"].max(), 1)
        ),
        "high_balance_disengagement_rate": (
            float(1 - high_balance["IsActiveMember"].mean())
            if not high_balance.empty else 0.0
        ),
        "credit_card_stickiness_score": (
            float(1 - cardholders["Exited"].mean()) if not cardholders.empty else 0.0
        ),
        "relationship_strength_index": float(
            data["RelationshipStrengthIndex"].mean()
        ),
    }

def apply_filters(
    data: pd.DataFrame,
    geographies: list[str],
    genders: list[str],
    age_range: tuple[int, int],
    tenure_range: tuple[int, int],
    products: list[int],
    balance_range: tuple[float, float],
) -> pd.DataFrame:
    """Apply all dashboard filters in one deterministic operation."""
    mask = (
        data["Geography"].isin(geographies)
        & data["Gender"].isin(genders)
        & data["Age"].between(*age_range)
        & data["Tenure"].between(*tenure_range)
        & data["NumOfProducts"].isin(products)
        & data["Balance"].between(*balance_range)
    )
    return data.loc[mask].copy()

def grouped_metrics(data: pd.DataFrame, group: str) -> pd.DataFrame:
    """Return count, churn, activity and relationship metrics by a dimension."""
    return (
        data.groupby(group, observed=False)
        .agg(
            Customers=("CustomerId", "count"),
            ChurnRate=("Exited", "mean"),
            RetentionRate=("Exited", lambda x: 1 - x.mean()),
            ActiveRate=("IsActiveMember", "mean"),
            AverageProducts=("NumOfProducts", "mean"),
            AverageBalance=("Balance", "mean"),
            RelationshipStrength=("RelationshipStrengthIndex", "mean"),
        )
        .reset_index()
    )
