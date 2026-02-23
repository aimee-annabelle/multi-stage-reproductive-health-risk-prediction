"""Stage 05: Hyperparameter tuning for infertility v1."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold

sns.set_theme(style="whitegrid")

SPLIT_DIR = Path("data/processed/infertility_v1_splits")
ML_DIR = Path("ml")
OUTPUT_DIR = Path("evaluation/infertility_v1/tuning")

TARGET_COLUMN = "Infertility_Prediction"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def flatten_cv_results(df: pd.DataFrame) -> pd.DataFrame:
    keep_cols = [
        "mean_test_score",
        "std_test_score",
        "rank_test_score",
        "param_n_estimators",
        "param_max_depth",
        "param_min_samples_leaf",
        "param_min_samples_split",
        "param_max_features",
    ]
    existing = [c for c in keep_cols if c in df.columns]
    return df[existing].sort_values("rank_test_score")


def plot_top_results(results_df: pd.DataFrame, file_name: str) -> None:
    top = results_df.nsmallest(12, "rank_test_score").copy()
    top["config"] = [f"#{i+1}" for i in range(len(top))]

    plt.figure(figsize=(9, 5))
    sns.barplot(data=top, x="config", y="mean_test_score", color="#54a24b")
    plt.title("Top CV Configurations (F1)")
    plt.ylim(0.0, 1.0)
    plt.xlabel("Configuration")
    plt.ylabel("Mean CV F1")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / file_name, dpi=160)
    plt.close()


def main() -> None:
    ensure_dirs()

    train_df = pd.read_csv(SPLIT_DIR / "train_scaled.csv")
    test_df = pd.read_csv(SPLIT_DIR / "test_scaled.csv")

    X_train = train_df.drop(columns=[TARGET_COLUMN])
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test = test_df[TARGET_COLUMN]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scorer = make_scorer(f1_score)

    base_model = RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=1)

    random_space = {
        "n_estimators": [100, 200, 300, 400, 500],
        "max_depth": [4, 6, 8, 10, None],
        "min_samples_split": [2, 4, 6, 8, 10],
        "min_samples_leaf": [1, 2, 3, 4, 5],
        "max_features": ["sqrt", "log2", None],
    }

    random_search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=random_space,
        n_iter=40,
        scoring=scorer,
        cv=cv,
        random_state=42,
        n_jobs=1,
        verbose=0,
        refit=True,
    )
    random_search.fit(X_train, y_train)

    random_results = flatten_cv_results(pd.DataFrame(random_search.cv_results_))
    random_results.to_csv(OUTPUT_DIR / "random_search_results.csv", index=False)
    plot_top_results(random_results, "random_search_top_configs.png")

    best = random_search.best_params_
    grid_space = {
        "n_estimators": sorted({max(100, best["n_estimators"] - 100), best["n_estimators"], best["n_estimators"] + 100}),
        "max_depth": sorted({best["max_depth"], 8, 10}, key=lambda x: (x is None, x)),
        "min_samples_split": sorted({max(2, best["min_samples_split"] - 2), best["min_samples_split"], best["min_samples_split"] + 2}),
        "min_samples_leaf": sorted({max(1, best["min_samples_leaf"] - 1), best["min_samples_leaf"], best["min_samples_leaf"] + 1}),
        "max_features": list({best["max_features"], "sqrt", "log2"}),
    }

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=grid_space,
        scoring=scorer,
        cv=cv,
        n_jobs=1,
        verbose=0,
        refit=True,
    )
    grid_search.fit(X_train, y_train)

    grid_results = flatten_cv_results(pd.DataFrame(grid_search.cv_results_))
    grid_results.to_csv(OUTPUT_DIR / "grid_search_results.csv", index=False)
    plot_top_results(grid_results, "grid_search_top_configs.png")

    tuned_model = grid_search.best_estimator_
    tuned_model.fit(X_train, y_train)
    test_f1 = f1_score(y_test, tuned_model.predict(X_test))

    joblib.dump(tuned_model, ML_DIR / "infertility_model_tuned.pkl")

    summary = {
        "random_search_best_params": random_search.best_params_,
        "random_search_best_cv_f1": float(random_search.best_score_),
        "grid_search_best_params": grid_search.best_params_,
        "grid_search_best_cv_f1": float(grid_search.best_score_),
        "tuned_test_f1": float(test_f1),
        "model_output": str(ML_DIR / "infertility_model_tuned.pkl"),
        "bayesian_optimization": "not_run (dependency not included in project requirements)",
    }
    (OUTPUT_DIR / "tuning_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Hyperparameter tuning complete. Summary saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
