"""
ORACLE-26 — XGBoost Match Classifier
=======================================
Predicts Win/Draw/Loss probabilities based on engineered feature differences.
Acts as the secondary ML layer in the ORACLE-26 ensemble.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
import joblib
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

class XGBoostModel:
    """
    XGBoost Classifier for match outcomes (0: Loss, 1: Draw, 2: Win).
    """

    def __init__(self, model_params: Optional[dict] = None):
        self.params = model_params or {
            "objective": "multi:softprob",
            "num_class": 3,
            "max_depth": 4,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42
        }
        self.model = xgb.XGBClassifier(**self.params)
        self.is_fitted = False
        self.feature_names = []

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fit the model on feature differences.
        y should be 0 (Away Win), 1 (Draw), 2 (Home Win).
        """
        print(f"  [xgboost] Training on {len(X)} matches...")
        self.feature_names = X.columns.tolist()
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict_match(self, team1_features: dict, team2_features: dict) -> dict:
        """
        Predict probabilities for a specific match.
        Calculates differences (T1 - T2) and passes to model.
        """
        if not self.is_fitted:
            # Baseline probabilities if not fitted
            return {"win_prob": 0.4, "draw_prob": 0.25, "loss_prob": 0.35}

        # Create difference vector
        diff = {}
        for feat in self.feature_names:
            # Assumes features are passed as standard names (e.g., 'elo')
            if feat in team1_features and feat in team2_features:
                diff[feat] = team1_features[feat] - team2_features[feat]
            else:
                diff[feat] = 0.0

        X_test = pd.DataFrame([diff])
        probs = self.model.predict_proba(X_test)[0]

        return {
            "win_prob":  round(float(probs[2]), 3),
            "draw_prob": round(float(probs[1]), 3),
            "loss_prob": round(float(probs[0]), 3),
        }

    def save(self, path: str = "models/xgboost_model.pkl"):
        joblib.dump({"model": self.model, "features": self.feature_names, "fitted": self.is_fitted}, path)
        print(f"  [xgboost] Model saved → {path}")

    @classmethod
    def load(cls, path: str = "models/xgboost_model.pkl") -> "XGBoostModel":
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.feature_names = data["features"]
        instance.is_fitted = data["fitted"]
        print(f"  [xgboost] Model loaded from {path}")
        return instance

if __name__ == "__main__":
    # Placeholder for local testing
    print("XGBoost Model module initialized.")
