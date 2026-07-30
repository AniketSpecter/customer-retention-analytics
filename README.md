# Customer Engagement & Product Utilization Analytics for Retention Strategy

A complete customer-retention analytics project built with Python, Streamlit and machine learning.

## Prepared by

**Aniket Chakraborty**

## Project overview

The project analyzes 10,000 European bank customer records to examine how customer activity, product depth, account balance and relationship strength are associated with historical churn. It includes an interactive dashboard, customer segmentation, premium-customer risk analysis and a fairness-aware Random Forest churn-risk model.

## Key results

- Historical churn rate: **20.37%**
- Historical retention rate: **79.63%**
- Germany churn rate: **32.44%**
- Inactive-customer churn rate: **26.85%**
- Active-customer churn rate: **14.27%**
- Two-product customers have the strongest historical retention
- Model ROC AUC: **0.8545**

## Dashboard modules

1. **Executive Overview** - retention, activity and relationship KPIs
2. **Engagement** - engagement profiles and activity/product heatmaps
3. **Product Utilization** - product-depth and card-stickiness analysis
4. **Premium Risk** - high-balance customer risk and priority queue
5. **Churn Model** - evaluation, feature importance and risk simulator
6. **Customer Explorer** - customer-level search and CSV export

## Repository structure

```text
customer-retention-analytics/
├── app.py
├── analytics.py
├── modeling.py
├── requirements.txt
├── README.md
├── DATA_DICTIONARY.md
├── PROJECT_MANIFEST.txt
├── Customer_Retention_Analysis.ipynb
├── Customer_Retention_Analysis_Executed.ipynb
├── data/
│   └── European_Bank.csv
├── docs/
│   ├── Customer_Retention_Analytics_Research_Report.pdf
│   ├── Customer_Retention_Analytics_Research_Report.docx
│   ├── Customer_Retention_Executive_Summary.pdf
│   └── Customer_Retention_Executive_Summary.docx
├── results/
│   └── analysis outputs and customer priority files
└── assets/
    └── report charts
```

## Run locally on Windows

### One-click method

Double-click:

```text
run_dashboard.bat
```

### Manual method

```powershell
git clone https://github.com/AniketSpecter/customer-retention-analytics.git
cd customer-retention-analytics
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run locally on Linux or macOS

```bash
git clone https://github.com/AniketSpecter/customer-retention-analytics.git
cd customer-retention-analytics
chmod +x run_dashboard.sh
./run_dashboard.sh
```

## Deploy on Streamlit Community Cloud

Use these settings:

```text
Repository: AniketSpecter/customer-retention-analytics
Branch: main
Main file path: app.py
```

The dataset is loaded from `data/European_Bank.csv`; keep that path unchanged.

## KPI definitions

- **Engagement Retention Ratio:** retention among active customers.
- **Product Depth Index:** average product count divided by the maximum observed product count.
- **High-Balance Disengagement Rate:** inactive share among top-quartile balance customers.
- **Credit-Card Stickiness Score:** retention among credit-card holders.
- **Relationship Strength Index:** transparent 0-100 composite using activity, product configuration, tenure, card ownership and balance commitment.

## Model governance

`Gender` is excluded from operational prediction and retained only for descriptive fairness monitoring. The model is intended to prioritize human review and controlled retention outreach, not automate adverse customer decisions.

## Research paper

The submission-ready paper is available at:

```text
docs/Customer_Retention_Analytics_Research_Report.pdf
```

## Limitations

The dataset is historical and cross-sectional. The results identify associations rather than proving causation. Retention actions should be validated through controlled pilots.
