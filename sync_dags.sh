#!/bin/bash

DEV_DAG_DIR="./airflow/dev-dags"
PROD_DAG_DIR="./airflow/dags"

echo "Copying DAGs from dev-dags to dags..."
cp $DEV_DAG_DIR/*.py $PROD_DAG_DIR/

echo "Adding all changes to Git..."
git add .

echo "Enter commit message:"
read COMMIT_MSG

git commit -m "$COMMIT_MSG"

echo "Pushing to GitHub..."
git push origin main

echo "? Sync completed successfully!"
