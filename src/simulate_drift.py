import json
import os
import pandas as pd
import numpy as np

def simulate_data_drift():
    # Ensure the shared data directory exists
    os.makedirs("data", exist_ok=True)
    
    # 1. Generate fake drifted production data for the retraining script
    print("Generating synthetic drifted customer data...")
    np.random.seed(42)
    
    # Simulating 1000 new customer records with shifting distributions
    data = {
        "Tenure": np.random.randint(1, 72, 1000),
        "MonthlyCharges": np.random.uniform(20.0, 120.0, 1000),
        "TotalCharges": np.random.uniform(20.0, 8000.0, 1000),
        "Churn": np.random.choice([0, 1], 1000, p=[0.6, 0.4]) # Artificially high churn rate
    }
    df = pd.DataFrame(data)
    df.to_csv("data/current_data.csv", index=False)
    print("✅ Saved drifted dataset to data/current_data.csv")

    # 2. Create the JSON report to trigger the Airflow logic gate
    report_path = "data/drift_report.json"
    mock_report = {
        "drift_detection": True,
        "drifted_features": ["MonthlyCharges", "Churn"],
        "drift_score": 0.82
    }
    
    with open(report_path, "w") as f:
        json.dump(mock_report, f, indent=4)
        
    print(f"✅ Simulated drift report written to {report_path}")
    print("-" * 45)
    print("System is primed! Trigger the Airflow DAG to watch the retraining sequence.")

if __name__ == "__main__":
    simulate_data_drift()