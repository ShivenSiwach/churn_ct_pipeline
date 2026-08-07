import pandas as pd
import json
import os
from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset

def run_drift_check():
    ref_path = "data/train.csv"
    curr_path = "data/current_data.csv"
    report_path = "data/drift_report.json"

    if not os.path.exists(ref_path) or not os.path.exists(curr_path):
        raise FileNotFoundError("Ensure both data/train.csv and data/current_data.csv exist.")

    # Load reference (baseline) and current (incoming) datasets
    ref_data = pd.read_csv(ref_path)
    curr_data = pd.read_csv(curr_path)

    # Drop target column 'Churn' if present to focus strictly on feature drift
    for df in [ref_data, curr_data]:
        if "Churn" in df.columns:
            df.drop("Churn", axis=1, inplace=True) 

    # Run evidently data drift test suite
    drift_suite = TestSuite(tests=[DataDriftTestPreset()])
    drift_suite.run(reference_data=ref_data, current_data=curr_data)

    # Export dictionary output
    suite_result = drift_suite.as_dict()
    all_passed = suite_result["summary"]["all_passed"]

    # Structure JSON report for downstream orchestrators (Airflow)
    output_summary = {
        "drift_detection": not all_passed,
        "total_tests": suite_result["summary"]["total_tests"],
        "failed_tests": suite_result["summary"]["failed_tests"]
    }

    with open(report_path, "w") as f:
        json.dump(output_summary, f, indent=4)

    print("----")
    print("Drift Evaluation Finished.")
    print(f"Drift Detected: {not all_passed}")
    print(f"Report written to '{report_path}'.")
    print("----")

if __name__ == "__main__":
    run_drift_check()