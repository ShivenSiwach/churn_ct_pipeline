# Automated Continuous Training (CT) Pipeline for Customer Churn Prediction

An enterprise-grade MLOps architecture designed to autonomously monitor production data for statistical drift and trigger machine learning retraining workflows. This project shifts focus from static data science to resilient, automated infrastructure using Docker, Apache Airflow, and MLflow.

## 🏗️ System Architecture & Tech Stack

*   **Orchestration:** Apache Airflow 2.9.1 (LocalExecutor)[cite: 1]
*   **Database Backend:** PostgreSQL 13[cite: 1]
*   **Experiment Tracking:** MLflow
*   **Machine Learning:** Python 3.11, XGBoost, Scikit-learn, Pandas[cite: 1]
*   **Infrastructure:** Docker Compose, Dockerfile[cite: 1]

## 🚀 Key Features (Phases 1-3 Completed)

1.  **Data Drift Monitoring:** Evaluates incoming production data against a training baseline to detect statistical distribution shifts. Generates a `drift_report.json` to inform the pipeline.
2.  **Intelligent Orchestration (Airflow):** Utilizes a `BranchPythonOperator` as a logic gate. If drift is detected, the DAG routes to the model retraining sequence; if no drift is found, it gracefully skips the heavy ML tasks to save compute resources.
3.  **Automated Experiment Tracking (MLflow):** When retraining is triggered, candidate XGBoost models are trained, and all hyperparameters, evaluation metrics (AUC-ROC 0.83, F1 0.58)[cite: 2], and artifacts are automatically logged to a local MLflow tracking server.

## 🛠️ System Design & Engineering Challenges

### Resolving Airflow Container Boot Bottlenecks
During the initial deployment, the Airflow webserver failed to bind to port `8080`, returning an `ERR_EMPTY_RESPONSE` while consuming 119.8% CPU[cite: 1]. 

**Root Cause:** The pipeline relied on Airflow's `_PIP_ADDITIONAL_REQUIREMENTS` environment variable to install heavy ML dependencies (`pandas`, `xgboost`, `scikit-learn`, `mlflow`, `evidently`) at every container startup[cite: 1]. This forced an extensive build process that prevented the webserver from launching in time[cite: 1].

**Solution:** Transitioned the architecture to a custom `Dockerfile` that bakes all dependencies (including a strictly pinned `cryptography==41.0.7` library to resolve internal version conflicts) directly into the image layer[cite: 1]. This reduced container startup time from several minutes to under 30 seconds and permanently stabilized the pipeline[cite: 1].

## 💻 How to Run Locally

### 1. Start the Infrastructure
Ensure Docker Desktop is running, then build and start the containerized environment:
```bash
# Clean up any stale volumes
docker-compose down -v

# Build the custom image and spin up the Airflow/Postgres stack
docker-compose up -d --build
2. Access the Airflow UI
Wait ~30 seconds for the database migrations to complete, then navigate to:

URL: http://127.0.0.1:9090

Username: admin

Password: admin

3. Simulate Data Drift
To see the continuous training loop in action, run the simulation script to generate drifted synthetic data and trigger the Airflow logic gate:

Bash
python src/simulate_drift.py
Trigger the continuous_training_pipeline DAG in the Airflow UI and watch the retrain_model task execute.

4. View MLflow Artifacts
To review the newly trained XGBoost model and its performance metrics, temporarily allow file-store tracking and boot the MLflow server:

PowerShell
# Windows PowerShell command
$env:MLFLOW_ALLOW_FILE_STORE="true"
mlflow ui --host 127.0.0.1 --port 5000
Navigate to http://127.0.0.1:5000 to view the continuous-training-pipeline experiment logs.

🔜 Future Work (Phase 4)
Zero-Downtime Deployment: Wrapping the new champion models in a FastAPI service and implementing a Blue/Green deployment strategy using an Nginx reverse proxy to swap containers without dropping live user requests.