from __future__ import annotations

import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


FEATURE_COLUMNS = [
    "liquidity_score",
    "quality_score",
    "momentum_score",
    "risk_score",
    "volatility_30d",
    "dividend_yield",
]

LABEL_MAP = {"SELL": 0, "HOLD": 1, "BUY": 2}
INVERSE_LABEL_MAP = {value: key for key, value in LABEL_MAP.items()}


def train_signal_model(frame: pd.DataFrame) -> tuple[XGBClassifier, dict]:
    """Train an offline signal classifier from labeled research outcomes."""
    missing = set(FEATURE_COLUMNS + ["signal"]).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing training columns: {', '.join(sorted(missing))}")

    x = frame[FEATURE_COLUMNS].astype(float)
    y = frame["signal"].map(LABEL_MAP)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if y.nunique() > 1 else None,
    )

    model = XGBClassifier(
        objective="multi:softprob",
        eval_metric="mlogloss",
        max_depth=3,
        n_estimators=80,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return model, report
