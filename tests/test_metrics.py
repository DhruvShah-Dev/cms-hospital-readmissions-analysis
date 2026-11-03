from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_clean_dataset import clean_hrrp, priority_category  # noqa: E402


def test_estimated_excess_readmissions_uses_rate_gap_and_preserves_missing() -> None:
    raw = pd.DataFrame(
        {
            "Facility Name": ["A", "B", "C"],
            "Facility ID": ["000001", "000002", "000003"],
            "State": ["NY", "NY", "NY"],
            "Measure Name": ["READM-30-HF-HRRP"] * 3,
            "Number of Discharges": ["100", "100", "Too Few to Report"],
            "Excess Readmission Ratio": ["1.1", "0.9", "Not Available"],
            "Predicted Readmission Rate": ["12", "9", "Not Available"],
            "Expected Readmission Rate": ["10", "10", "Not Available"],
            "Number of Readmissions": ["12", "9", "Too Few to Report"],
            "Start Date": ["07/01/2021"] * 3,
            "End Date": ["06/30/2024"] * 3,
            "Footnote": [None, None, "Too few cases"],
        }
    )

    clean = clean_hrrp(raw)

    assert clean.loc[0, "estimated_excess_readmissions"] == 2.0
    assert clean.loc[0, "positive_estimated_excess_readmissions"] == 2.0
    assert clean.loc[1, "estimated_excess_readmissions"] == -1.0
    assert clean.loc[1, "positive_estimated_excess_readmissions"] == 0.0
    assert pd.isna(clean.loc[2, "estimated_excess_readmissions"])
    assert pd.isna(clean.loc[2, "positive_estimated_excess_readmissions"])


def test_priority_bands_and_missing_are_distinct() -> None:
    values = pd.Series([np.nan, -1, 0, 4.99, 5, 19.99, 20])
    result = priority_category(values)

    assert pd.isna(result.iloc[0])
    assert result.iloc[1:].tolist() == [
        "No Estimated Excess",
        "No Estimated Excess",
        "Monitor",
        "High",
        "High",
        "Critical",
    ]


def test_processed_dataset_core_invariants() -> None:
    path = ROOT / "data" / "processed" / "hospital_readmissions_analytic.csv"
    df = pd.read_csv(path, dtype={"facility_id": "string"}, low_memory=False)

    assert len(df) == 18_330
    assert not df.duplicated(["facility_id", "measure_name"]).any()
    assert df["excess_readmission_ratio"].notna().sum() == 11_720
    assert df["estimated_excess_readmissions"].notna().sum() == 8_037
    assert np.isclose(
        df["positive_estimated_excess_readmissions"].sum(),
        12_245.489635,
        rtol=0,
        atol=1e-6,
    )
