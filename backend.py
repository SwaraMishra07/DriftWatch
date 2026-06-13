import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

# -------------------------------
# Split Data (Chronological if possible)
# -------------------------------
def split_data(data):

    # If timestamp exists → sort
    time_cols = [col for col in data.columns if "time" in col.lower() or "date" in col.lower()]

    if time_cols:
        data = data.sort_values(time_cols[0])
        split_idx = int(0.7 * len(data))
        train = data.iloc[:split_idx]
        new = data.iloc[split_idx:]
    else:
        train = data.sample(frac=0.7, random_state=42)
        new = data.drop(train.index)

    return train, new


# -------------------------------
# Preprocessing
# -------------------------------
def preprocess_data(data):

    data = data.copy()

    for col in data.columns:

        if "time" in col.lower() or "date" in col.lower():
            data[col] = pd.to_datetime(data[col], errors="coerce")
            data[col] = data[col].view("int64") // 10**9
            data[col] = data[col].fillna(0)

        elif data[col].dtype == "object":
            coerced = pd.to_numeric(data[col], errors="coerce")
            if coerced.notna().any() and coerced.isna().sum() < len(coerced) * 0.1:
                data[col] = coerced
            else:
                data[col] = data[col].astype("category")

    return data


# -------------------------------
# Optional Drift Simulation
# -------------------------------
def simulate_drift(new, strength=1.3):

    new = new.copy()

    for col in new.columns:

        if pd.api.types.is_numeric_dtype(new[col]):
            new[col] = new[col] * np.random.uniform(1.1, strength)

        elif pd.api.types.is_categorical_dtype(new[col]):
            new[col] = new[col].sample(frac=1).values

    return new


# -------------------------------
# PSI (Numeric)
# -------------------------------
def calculate_psi(expected, actual, bins=10):

    expected = expected.dropna()
    actual = actual.dropna()

    if len(expected) < 5 or len(actual) < 5:
        return 0

    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))

    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]

    expected_perc = expected_counts / len(expected)
    actual_perc = actual_counts / len(actual)

    psi = np.sum(
        (expected_perc - actual_perc) *
        np.log((expected_perc + 1e-6) / (actual_perc + 1e-6))
    )

    return psi


# -------------------------------
# Categorical Drift (PSI style)
# -------------------------------
def categorical_drift(train, new):

    train_dist = train.value_counts(normalize=True)
    new_dist = new.value_counts(normalize=True)

    categories = set(train_dist.index).union(set(new_dist.index))

    drift = 0
    for cat in categories:
        p = train_dist.get(cat, 1e-6)
        q = new_dist.get(cat, 1e-6)
        drift += (p - q) * np.log((p + 1e-6) / (q + 1e-6))

    return drift


# -------------------------------
# Feature Drift
# -------------------------------
def calculate_feature_drift(train, new):

    drift_results = {}

    for col in train.columns:

        # Skip constant columns
        if train[col].nunique() <= 1:
            continue

        # NUMERIC
        if pd.api.types.is_numeric_dtype(train[col]):

            mean_diff = abs(train[col].mean() - new[col].mean())
            norm_mean_diff = mean_diff / (train[col].std() + 1e-6)

            psi = calculate_psi(train[col], new[col])

            # KS test
            ks_stat, p_value = ks_2samp(train[col], new[col])

            drift_score = 0.6 * psi + 0.4 * norm_mean_diff

        # CATEGORICAL
        else:

            psi = categorical_drift(train[col], new[col])
            norm_mean_diff = psi
            ks_stat, p_value = 0, 1
            drift_score = psi

        drift_results[col] = {
            "mean_diff": round(norm_mean_diff, 4),
            "psi": round(psi, 4),
            "ks_stat": round(ks_stat, 4),
            "p_value": round(p_value, 4),
            "drift_score": round(drift_score, 4)
        }

    return drift_results


# -------------------------------
# Overall Drift
# -------------------------------
def calculate_overall_drift(drift_results):

    if not drift_results:
        return 0

    scores = [v["drift_score"] for v in drift_results.values()]
    return np.mean(scores)


# -------------------------------
# Classification (PSI based)
# -------------------------------
def classify_drift(score):

    if score < 0.1:
        return "Low Drift"
    elif score < 0.25:
        return "Medium Drift"
    else:
        return "High Drift"


# -------------------------------
# Top Feature
# -------------------------------
def get_top_feature(drift_results):

    if not drift_results:
        return None

    return max(drift_results, key=lambda x: drift_results[x]["drift_score"])


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def detect_drift(data, simulate=False):

    data = preprocess_data(data)

    train, new = split_data(data)

    if simulate:
        new = simulate_drift(new)

    drift_results = calculate_feature_drift(train, new)

    overall_score = calculate_overall_drift(drift_results)
    status = classify_drift(overall_score)
    top_feature = get_top_feature(drift_results)

    return {
        "overall_score": round(overall_score, 4),
        "status": status,
        "feature_drift": drift_results,
        "top_feature": top_feature,
        "train": train,
        "new": new
    }