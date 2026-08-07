import pandas as pd
import numpy as np
import os

def create_drifted_data():
   input_path = "data/test.csv"
   output_path = "data/current_data.csv"

   if not os.path.exists(input_path):
      raise FileNotFoundError(f"Missing baseline file: {input_path}. Please place test.csv in the data/ directory.")

   # Load baseline test data
   df = pd.read_csv(input_path)
   np.random.seed(42)

   # 1. Simulate price hikes: Increase avg_monthly_spend by 30%
   if "avg_monthly_spend" in df.columns:
      df["avg_monthly_spend"] = df["avg_monthly_spend"] * 1.30

   # 2. Add noise to TotalCharges
   if "TotalCharges" in df.columns:
      noise = np.random.normal(loc=0, scale=200, size=len(df)) 
      df["TotalCharges"] = (df["TotalCharges"] + noise).clip(lower=0)

   # 3. Reduce tenure by 20% to simulate shorter lifespan
   if "tenure" in df.columns:
      df["tenure"] = (df["tenure"] * 0.8).astype(int)

   # save as new incoming production batch
   df.to_csv(output_path, index=False) 
   print(f"Drifted dataset successfullygenerated at '{output_path}'.")

if __name__ == "__main__":
   create_drifted_data()