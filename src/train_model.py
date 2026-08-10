import pandas as pd
import xgboost as xgb
import mlflow
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, f1_score

# Permanently bypass the MLflow database requirement for local testing
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

def retrain_model():
    data_path = "data/current_data.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing data: {data_path}. Run simulate_drift.py first.")

    # 1. Load the new drifted production data
    df = pd.read_csv(data_path)
    
    # 2. Separate features and target
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    # 3. Create a fresh Validation Split to evaluate the new model
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Calculate class imbalance for XGBoost
    neg_class = (y_train == 0).sum()
    pos_class = (y_train == 1).sum()
    scale_weight = neg_class / pos_class

    # 4. Set up MLflow Tracking
    mlflow.set_experiment("continuous-training-pipeline")
    mlflow.xgboost.autolog() # Automatically tracks params, metrics, and artifacts

    print("Initiating XGBoost retraining sequence...")
    
    with mlflow.start_run(run_name="drift_reaction_retrain"):
        # 5. Initialize and Train the Model
        model = xgb.XGBClassifier(
            n_estimators=100,
            scale_pos_weight=scale_weight,
            random_state=42,
            eval_metric="logloss"
        )
        
        model.fit(X_train, y_train)

        # 6. Evaluate the new model on the validation split
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, probs)
        f1 = f1_score(y_test, preds)

        # Manually log the primary metrics we care about for the deployment gate
        mlflow.log_metric("validation_auc_roc", auc)
        mlflow.log_metric("validation_f1_score", f1)

        # 7. Save the model so the FastAPI service can load it
        model.save_model("data/model.pkl")
        print(" Model serialized and saved to data/model.pkl")

        print("-" * 40)
        print("Retraining Complete!")
        print(f"New Model AUC-ROC: {auc:.4f}")
        print(f"New Model F1-Score:  {f1:.4f}")
        print("Artifacts successfully logged to MLflow Local Registry.")
        print("-" * 40)

if __name__ == "__main__":
    retrain_model()