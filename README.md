# MLOps Pipeline Portfolio

End-to-end MLOps coursework: turning a raw Airbnb listings dataset into a served, monitored,
and Kubernetes-deployed model. Each module below is self-contained, with its own README,
Docker setup, and (where relevant) screenshots of the running system.

**Stack:** Docker · DVC · Apache Airflow · MLflow · FastAPI · PostgreSQL · Qdrant · MinIO · Kubernetes (k3s)

---

## Structure

### 01 · Data Pipeline & Orchestration
| Module | What it does |
|---|---|
| [`01a-dockerized-etl`](01-airflow-data-pipeline/01a-dockerized-etl) | Dockerized, DVC-tracked ETL package that cleans and transforms raw listings data; packaged as an installable CLI (`airbnb-ops`) |
| [`01b-sql-performance-tuning`](01-airflow-data-pipeline/01b-sql-performance-tuning) | Query optimization: baseline `EXPLAIN ANALYZE`, a materialized view, and a Metabase dashboard on top |
| [`01c-airflow-orchestration`](01-airflow-data-pipeline/01c-airflow-orchestration) | Airflow DAG that orchestrates the ETL pipeline end to end |

### 02 · Experiment Tracking & Serving
| Module | What it does |
|---|---|
| [`02a-feature-pipeline`](02-experiment-tracking-and-serving/02a-feature-pipeline) | Feature engineering pipeline with schema validation and a PII audit report |
| [`02b-mlflow-experiments`](02-experiment-tracking-and-serving/02b-mlflow-experiments) | Eight tracked model runs in MLflow (dummy baseline → leaky vs. clean logistic regression → class-balanced → threshold-tuned → random forest), each with confusion matrices and classification reports |
| [`02c-fastapi-model-serving`](02-experiment-tracking-and-serving/02c-fastapi-model-serving) | FastAPI service serving the best MLflow-tracked model, with request validation (rejects leakage fields, missing fields, wrong types) and Swagger docs |

### 03 · Containers & Kubernetes
| Module | What it does |
|---|---|
| [`03a-dockerized-serving`](03-containers-and-kubernetes/03a-dockerized-serving) | Model-serving API with a naive vs. optimized Dockerfile comparison (image size report) and a first Kubernetes deployment |
| [`03b-versioned-model-bundle`](03-containers-and-kubernetes/03b-versioned-model-bundle) | Hash-pinned, versioned bundle of a sentence-transformers encoder — SHA-256 manifest, registered in MLflow, uploaded to MinIO |
| [`03c-embedding-search-service`](03-containers-and-kubernetes/03c-embedding-search-service) | Embedding + semantic search microservice: FastAPI in front of Qdrant (vector search), Postgres, and MinIO |
| [`03d-k8s-deployment-strategies`](03-containers-and-kubernetes/03d-k8s-deployment-strategies) | Deploying the service to a real k3s cluster: rolling updates, blue-green deploys, horizontal pod autoscaling, pod disruption budgets, ConfigMaps/Secrets, and graceful shutdown (`preStop` hooks) |

---

## Notes

- This repo was built as part of an applied MLOps bootcamp; it uses a shared course
  database/cluster for some modules, so a handful of scripts expect course-provided
  environment variables rather than public endpoints.
- Large model artifacts are tracked with DVC rather than committed directly.
- Each module folder has its own `README.md` with setup and run instructions.
