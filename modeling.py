from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

MODEL_FEATURES = [
    "CreditScore", "Geography", "Age", "Tenure", "Balance",
    "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary"
]
NUMERIC_FEATURES = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "EstimatedSalary"
]
CATEGORICAL_FEATURES = ["Geography", "HasCrCard", "IsActiveMember"]

def build_model() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

def train_and_evaluate(data: pd.DataFrame):
    """Train with a stratified holdout, then refit on all data for operations."""
    X = data[MODEL_FEATURES]
    y = data["Exited"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    evaluation_model = build_model()
    evaluation_model.fit(X_train, y_train)
    probabilities = evaluation_model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.50).astype(int)
    metrics = {
        "ROC AUC": roc_auc_score(y_test, probabilities),
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions),
        "Recall": recall_score(y_test, predictions),
        "F1 Score": f1_score(y_test, predictions),
    }

    operational_model = build_model()
    operational_model.fit(X, y)
    return operational_model, metrics

def feature_importance(model: Pipeline) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocessor"]
    names = list(NUMERIC_FEATURES)
    encoder = (
        preprocessor.named_transformers_["categorical"]
        .named_steps["encoder"]
    )
    names.extend(encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist())
    values = model.named_steps["classifier"].feature_importances_
    return (
        pd.DataFrame({"Feature": names, "Importance": values})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )

def predict_customer(model: Pipeline, customer: dict) -> float:
    row = pd.DataFrame([customer], columns=MODEL_FEATURES)
    return float(model.predict_proba(row)[:, 1][0])
