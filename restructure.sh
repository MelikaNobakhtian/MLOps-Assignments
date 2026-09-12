#!/usr/bin/env bash
# ==============================================================
# Restructure MLOps-Assignments into a clean, portfolio-friendly
# layout. Run this from the ROOT of your local clone, AFTER you
# have scrubbed the secrets from history (see SECURITY_FIX.md).
#
# Usage:
#   cd MLOps-Assignments
#   bash restructure.sh
# ==============================================================
set -euo pipefail

echo "==> Creating new folder layout..."
mkdir -p 01-airflow-data-pipeline
mkdir -p 02-experiment-tracking-and-serving
mkdir -p 03-containers-and-kubernetes

echo "==> Moving Module 01 (Data Pipeline & Orchestration)..."
git mv "HW01/HW01_A" "01-airflow-data-pipeline/01a-dockerized-etl"
git mv "HW01/HW01_B" "01-airflow-data-pipeline/01b-sql-performance-tuning"
git mv "HW01/HW01_C" "01-airflow-data-pipeline/01c-airflow-orchestration"

echo "==> Moving Module 02 (Experiment Tracking & Serving)..."
git mv "HW02/HW_A" "02-experiment-tracking-and-serving/02a-feature-pipeline"
git mv "HW02/HW_B" "02-experiment-tracking-and-serving/02b-mlflow-experiments"
git mv "HW02/HW_C/student_hw03_fastapi_serving" "02-experiment-tracking-and-serving/02c-fastapi-model-serving"

echo "==> Moving Module 03 (Containers & Kubernetes)..."
git mv "HW03/01_model_serving_student" "03-containers-and-kubernetes/03a-dockerized-serving"
git mv "HW03/HW3_Student/HW3_Student/HW3_A" "03-containers-and-kubernetes/03b-versioned-model-bundle"
git mv "HW03/HW3_Student/HW3_Student/HW3_B" "03-containers-and-kubernetes/03c-embedding-search-service"
git mv "HW03/HW3_Student/HW3_Student/HW3_C" "03-containers-and-kubernetes/03d-k8s-deployment-strategies"

echo "==> Cleaning up now-empty legacy folders..."
rm -rf HW01 HW02 HW03

echo "==> Dropping in the new root README..."
# README.md should already be placed at repo root before running this script.

echo "==> Done. Review with 'git status', then:"
echo "    git add -A"
echo "    git commit -m 'Restructure: flatten and rename modules, add root README'"
echo "    git push"
