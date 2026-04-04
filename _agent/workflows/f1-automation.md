---
description: F1 Automation Workflow - Sync Results and Retrain Models
---

This workflow synchronizes the latest race results with the database, scrapes new sentiment data, and retrains the ML models to provide updated predictions.

// turbo
1. Synchronize recent race results to Supabase.
run_command: python3 sync_results.py

// turbo
2. Scrape latest F1 news sentiment.
run_command: python3 -m ml.scrape_news

// turbo
3. Retrain machine learning models with the new data.
run_command: python3 -m ml.train

// turbo
4. Export updated predictions to the application front-end.
run_command: python3 -m ml.export_predictions
