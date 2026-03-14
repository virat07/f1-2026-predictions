# The F1 2026 Prediction Model Pipeline

This document explains the architecture, execution flow, and learning methodologies for the dynamically-updating machine learning pipeline driving the F1 2026 predictions web app.

## Table of Contents
1. [Overview](#1-overview)
2. [Data Sources & Ingestion](#2-data-sources--ingestion)
3. [Model Training & Execution](#3-model-training--execution)
4. [Continuous Learning (Online Learning)](#4-continuous-learning-online-learning)
5. [Automated Execution (CI/CD)](#5-automated-execution-cicd)

---

## 1. Overview
Instead of relying on hardcoded pre-season predictions, this application leverages multiple live data pipelines ranging from historical F1 telemetry (on-track) to live news sentiment analysis (off-track) to automatically update and correct predictions over the course of the 2026 season.

Every week, the models ingest the latest race result alongside the week's news cycle to figure out who has the momentum, and immediately outputs updated probabilities for future races and the final championship standings.

## 2. Data Sources & Ingestion
The system relies on three distinct data sources corresponding to different proxy variables of a team's performance:

1. **Ergast F1 Database (`data/raw/`):** 
   * Provides historical data stretching back to 1950. 
   * Useful for establishing long-term baselines, such as which teams historically perform well at specific styles of tracks (e.g., street circuits vs. high-speed aero tracks).
2. **FastF1 Telemetry API (`fastf1-cache`):** 
   * The live link to the current season. 
   * Provides the official lap data and session results from the current (2026) active season immediately after a race concludes.
3. **News Sentiment & Off-Track Momentum (`scrape_news.py`):** 
   * The model scrapes the live RSS feeds of major F1 news organizations (like Motorsport.com and Google News). 
   * By utilizing NLP (Natural Language Processing) tools like `vaderSentiment`, it measures the compound sentiment (positivity vs. negativity) surrounding specific teams or drivers during an active race week. This establishes an "off-track momentum" score (e.g., if a team brings major upgrades they tend to have high positive sentiment, or if they have internal drama they have negative sentiment).

## 3. Model Training & Execution 
The pipeline relies on `scikit-learn`'s **Gradient Boosting Classifier**, which creates an ensemble of decision trees.

* **Features:** Examples include the Year, Chassis Constructor, Track Circuit Length, Driver, Current Points Base, and the newly integrated Off-Track Sentiment Score.
* **Logic Flow:**
  1. Iterate across all historical data inside the `SEASONS` range.
  2. For every race, feed the features into the gradient boosting trees.
  3. The model corrects its own errors iteratively by analyzing which trees guessed wrong on actual historical data and adjusting the weights (Gradient Boosting).

## 4. Continuous Learning (Online Learning)
The biggest strength of this machine learning pipeline is that it is not static. **It learns as 2026 progresses.**

For example, when the Australian Grand Prix finished, the script queried `fastf1` to read the true results. The ML model fed those new results directly back into the training data set, dramatically shifting the weights to heavily favor the teams that proved they had pace under the new 2026 regulations (e.g., Mercedes).

Similarly, the `update_standings.py` script aggregates the *actual* points that drivers have earned so far in 2026, and only projects the remaining future races, ensuring mathematically impossible scenarios are eliminated from the predictions.

## 5. Automated Execution (CI/CD)
You do not need to manually trigger these models. The entire pipeline runs autonomously via **GitHub Actions**.

### Execution Path:
Inside `.github/workflows/update-predictions.yml`, the system has a CRON job scheduled for **every Monday at 8:00 AM UTC** (the morning after a race weekend).

1. The Action spins up a headless Ubuntu machine.
2. It restores the 10GB `fastf1` cache to avoid hitting rate limits.
3. It installs the pipeline requirements (`pip install -r ml/requirements.txt`).
4. It executes the scraping script, model training script, and standings update script sequentially.
5. If the ML predictions changed the outcome in `public/ml-predictions.json`, the GitHub Action bot automatically commits and pushes the new data back to the `main` branch.
6. This git commit immediately triggers Vercel/Netlify to build and launch the newly updated React webpage. 
