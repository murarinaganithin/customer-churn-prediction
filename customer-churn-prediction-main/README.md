# 📉 Customer Churn Prediction Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Scikit-Learn](https://img.shields.io/badge/ScikitLearn-ML-orange) ![Statsmodels](https://img.shields.io/badge/Statsmodels-Stats-green) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📌 Project Overview

A telecom company is losing customers to competitors. Acquiring a new customer costs **5x more** than retaining an existing one. This project builds an end-to-end machine learning pipeline to predict which customers are likely to churn, enabling proactive retention strategies before customers leave.

Two notebooks are included:
- **`churn_prediction.ipynb`** — the full production pipeline
- **`churn_walkthrough.ipynb`** — a step-by-step learning notebook for collaborators and learners (see below)

---

## 🎯 Objectives

1. Identify the key drivers of customer churn
2. Build and compare multiple ML classification models
3. Select the best model based on business-relevant metrics
4. Segment customers by churn risk for targeted intervention
5. Generate actionable retention recommendations

---

## 🛠️ Tech Stack

- **Python 3.12**
  - `pandas`, `numpy` — data manipulation and feature engineering
  - `scikit-learn` — ML models, preprocessing, and evaluation
  - `statsmodels` — statistical inference, p-values, and odds ratios
  - `matplotlib`, `seaborn` — visualization
  - `joblib` — model serialization
- **Jupyter Notebook** — end-to-end pipeline and walkthrough
- **Dataset** — IBM Telco Customer Churn (Kaggle)

---

## 📂 Repository Structure

```
customer-churn-prediction/
│
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv   # Download from Kaggle (see below)
│
├── notebooks/
│   ├── churn_prediction.ipynb      # Full production pipeline
│   └── churn_walkthrough.ipynb     # Step-by-step learning notebook
│
├── models/
│   ├── churn_model_gb.pkl          # Saved Gradient Boosting model
│   └── scaler.pkl                  # Saved StandardScaler
│
├── outputs/
│   ├── churn_predictions.csv       # Scored customers with risk segments
│   ├── churn_distribution.png
│   ├── churn_by_category.png
│   ├── numeric_distributions.png
│   ├── correlation_heatmap.png
│   ├── confusion_matrix_lr.png
│   ├── roc_curves.png
│   ├── feature_importance.png
│   └── risk_segmentation.png
│
├── requirements.txt
└── README.md
```

---

## 🔄 Pipeline Stages

```
1. Data Loading & Exploration     → shape, types, missing values, churn rate
2. Exploratory Data Analysis      → distributions, churn by category, correlations
3. Data Cleaning                  → TotalCharges fix, binary encoding, NaN handling
4. Feature Engineering            → AvgMonthlySpend, TenureGroup, one-hot encoding
5. Train/Test Split               → 80/20 stratified split + StandardScaler
6. Baseline Model                 → Logistic Regression
7. Advanced Models                → Random Forest + Gradient Boosting
8. Statistical Inference          → Statsmodels Logit — p-values + odds ratios
9. Model Evaluation               → Accuracy, Precision, Recall, F1, ROC-AUC
10. Feature Importance            → Top 15 churn drivers
11. Risk Segmentation             → Low / Medium / High risk customer scoring
12. Export                        → Predictions CSV + saved model
```

---

## 📊 Model Results

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | ~80% | ~0.65 | ~0.55 | ~0.60 | ~0.85 |
| Random Forest | ~79% | ~0.63 | ~0.50 | ~0.56 | ~0.83 |
| **Gradient Boosting** | **~80%** | **~0.65** | **~0.57** | **~0.61** | **~0.85** |

**Best model: Gradient Boosting** — highest ROC-AUC and F1 score.

> **Why ROC-AUC over Accuracy?**
> Accuracy is misleading for imbalanced datasets. ROC-AUC measures how well the model ranks churners above non-churners regardless of threshold — a better fit for a business churn problem where catching real churners matters more than raw accuracy.

---

## 🔍 Customer Risk Segmentation

| Risk Segment | Customers | % of Base |
|---|---|---|
| Low Risk | 4,423 | 62.8% |
| Medium Risk | 1,661 | 23.6% |
| High Risk | 959 | 13.6% |

**High Risk Profile:** 959 customers averaging £81.16/month with only 6.9 months tenure — new, high-paying customers are the most likely to leave.

---

## 💡 Key Findings

- **Tenure** is the strongest churn predictor — new customers (0–12 months) churn most
- **Month-to-month contracts** have 3x higher churn rates than annual contracts
- **High monthly charges** correlate strongly with churn risk
- **Fiber optic internet** customers churn more than DSL customers
- **Electronic check** payment method carries the highest churn rate
- All top features are statistically significant (p < 0.05) confirmed by Statsmodels

## 🎯 Business Recommendations

1. **Onboarding program** — target new customers (0–12 months) with loyalty incentives during the highest risk window
2. **Contract upgrade offers** — push month-to-month High Risk customers toward annual contracts
3. **Fiber optic pricing review** — high charges + high churn = pricing friction that needs addressing
4. **Payment method campaign** — encourage electronic check users to switch to auto-pay
5. **Monthly scoring** — run this model every month and feed the High Risk list to the retention team

---

## 📖 For Learners & Collaborators

This project includes a dedicated step-by-step walkthrough notebook: **`notebooks/churn_walkthrough.ipynb`**

Unlike the main pipeline which runs end-to-end, the walkthrough is designed to be run **one cell at a time** with detailed explanations covering:

- **Why** each step is done, not just how
- The business logic behind each modeling decision
- Plain English explanations of every metric (Accuracy, Recall, ROC-AUC, F1)
- Why Recall matters more than Accuracy for churn problems
- What feature importance actually tells you about the business
- How to interpret p-values and odds ratios from Statsmodels
- The difference between overfitting and generalization

Whether you're learning ML for the first time or want to understand the thinking behind each decision, start with the walkthrough notebook.

---

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/murarinaganithin/customer-churn-prediction.git
cd customer-churn-prediction
```

### 2. Create and activate a virtual environment
```bash
conda create -n churn python=3.12 -y
conda activate churn
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the dataset
Download the Telco Customer Churn dataset from Kaggle:
👉 https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Place the CSV file here:
```
data/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

### 5. Update the base path
Open the notebook and update this line to match your system:
```python
BASE = r'C:\Users\YOUR_USERNAME\Desktop\customer-churn-prediction'
```

### 6. Run the notebook

**Option A — Full pipeline (production):**
```
Open notebooks/churn_prediction.ipynb → Run All Cells
```

**Option B — Step by step walkthrough (recommended for learners):**
```
Open notebooks/churn_walkthrough.ipynb → Run cell by cell
```

### 7. View outputs
After running, check the `outputs/` folder for:
- `churn_predictions.csv` — all 7,043 customers scored with risk segments
- `*.png` — all generated charts
- `models/churn_model_gb.pkl` — saved trained model ready for deployment

---

## 🔁 Using the Saved Model on New Data

Load and use the trained model without retraining:

```python
import joblib
import pandas as pd

# Load saved model and scaler
model  = joblib.load('models/churn_model_gb.pkl')
scaler = joblib.load('models/scaler.pkl')

# Score new customers (must match training feature structure)
churn_probabilities = model.predict_proba(new_data)[:, 1]
churn_predictions   = model.predict(new_data)
```

---

## 👤 Author

**Oluwasegun Raphael**
Data Scientist & Analyst
- 📧 ralpholuwashegun@gmail.com
- 🔗 [LinkedIn](http://linkedin.com/in/roe10)
- 💻 [GitHub](https://github.com/roe10)
- 🌐 [Portfolio](https://roe10.github.io)
