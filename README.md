Automated Continuous Training (CT) Pipeline for
Customer Churn Prediction

An enterprise-grade MLOps architecture designed to autonomously monitor production data for statistical
drift and trigger machine learning retraining workflows. This project shifts focus from static data science

to resilient, automated infrastructure using Docker, Apache Airflow, and MLflow, topped with a zero-
downtime deployment strategy.

System Architecture & Tech Stack
Orchestration: Apache Airflow 2.9.1 (LocalExecutor)
Database Backend: PostgreSQL 13
Experiment Tracking: MLflow
Machine Learning: Python 3.11, XGBoost, Scikit-learn, Pandas
Serving & Proxy: FastAPI, Uvicorn, Nginx
Infrastructure: Docker Compose, Dockerfile

Key Features (Phases 1-4 Completed)
Data Drift Monitoring: Evaluates incoming production data against a training baseline to detect
statistical distribution shifts. Generates a drift_report.json to inform the pipeline.
Intelligent Orchestration (Airflow): Utilizes a BranchPythonOperator as a logic gate. If drift is
detected, the DAG routes to the model retraining sequence; if no drift is found, it gracefully skips the
heavy ML tasks to save compute resources.
Automated Experiment Tracking (MLflow): When retraining is triggered, candidate XGBoost
models are trained, and all hyperparameters, evaluation metrics (AUC-ROC 0.83, F1 0.58), and
artifacts are automatically logged to a local MLflow tracking server.
Zero-Downtime Deployment (Blue/Green):
FastAPI Serving: Wrapped the champion XGBoost model in a highly performant FastAPI REST
service.
Reverse Proxy: Configured an Nginx traffic controller to manage live user requests.
•
•
•
•
•
•

1.

2.

3.

4.
◦

◦

Seamless Upgrades: Engineered a Blue/Green container swapping protocol. When the Airflow
pipeline trains a new model, it deploys to a passive container, and Nginx instantly reroutes traffic
( nginx -s reload ) ensuring zero dropped requests during the upgrade process.

System Design & Engineering Challenges

Resolving Airflow Container Boot Bottlenecks
During the initial deployment, the Airflow webserver failed to bind to port 8080 , returning an
ERR_EMPTY_RESPONSE while consuming 119.8% CPU.
Root Cause: The pipeline relied on Airflow's _PIP_ADDITIONAL_REQUIREMENTS environment variable
to install heavy ML dependencies ( pandas , xgboost , scikit-learn , mlflow ) at every container
startup. This forced an extensive build process that prevented the webserver from launching in time.
Solution: Transitioned the architecture to a custom Dockerfile that bakes all dependencies (including
a strictly pinned cryptography==41.0.7 library to resolve internal version conflicts) directly into the
image layer. This reduced container startup time from several minutes to under 30 seconds and
permanently stabilized the pipeline.

How to Run Locally
1. Start the Infrastructure (Airflow & DB)
Ensure Docker Desktop is running, then build and start the containerized environment:
# Clean up any stale volumes
docker-compose down -v
# Build the custom image and spin up the Airflow/Postgres stack
docker-compose up -d --build

2. Access the Airflow UI
Wait ~30 seconds for the database migrations to complete, then navigate to: * URL: http://
127.0.0.1:9090 * Username: admin * Password: admin
◦

3. Simulate Data Drift & Retrain
To see the continuous training loop in action, run the simulation script to generate drifted synthetic data
and trigger the Airflow logic gate:
python src/simulate_drift.py

Trigger the continuous_training_pipeline DAG in the Airflow UI and watch the retrain_model
task execute to generate data/model.pkl .
4. Test Zero-Downtime Deployment (Nginx & FastAPI)
Boot the API and proxy to serve the newly trained model:

# 1. Build the API and Nginx proxy images
docker build -f Dockerfile.api -t churn-api:v1 .
docker build -f Dockerfile.nginx -t nginx-proxy .
# 2. Run the 'Blue' API container and the Nginx proxy
docker run -d --name churn-api-blue -p 9095:8000 churn-api:v1
docker run -d --name reverse-proxy -p 80:80 nginx-proxy
Navigate to http://localhost/health to verify the proxy is successfully routing traffic to the Blue
container.

5. View MLflow Artifacts
To review the newly trained XGBoost model and its performance metrics:

# Windows PowerShell command
$env:MLFLOW_ALLOW_FILE_STORE="true"
mlflow ui --host 127.0.0.1 --port 5000
Navigate to http://127.0.0.1:5000 to view the continuous-training-pipeline experiment
logs.
