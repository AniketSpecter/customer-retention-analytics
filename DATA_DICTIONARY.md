# Data Dictionary

| Column | Description |
|---|---|
| Year | Dataset observation year |
| CustomerId | Unique customer identifier |
| Surname | Customer surname |
| CreditScore | Customer creditworthiness score |
| Geography | Customer country/market |
| Gender | Customer gender; used only for descriptive fairness monitoring |
| Age | Customer age |
| Tenure | Years with the bank |
| Balance | Account balance |
| NumOfProducts | Number of bank products |
| HasCrCard | Credit-card indicator: 1=yes, 0=no |
| IsActiveMember | Activity indicator: 1=active, 0=inactive |
| EstimatedSalary | Estimated annual salary |
| Exited | Historical churn target: 1=exited, 0=retained |

## Engineered fields

| Field | Description |
|---|---|
| RetentionStatus | Retained or Churned |
| ActivityStatus | Active or Inactive |
| CardStatus | Credit Card or No Credit Card |
| AgeBand | Age segmentation |
| EngagementSegment | Active Engaged, Active Low-Product, Inactive High-Balance, or Inactive Disengaged |
| RelationshipStrengthIndex | Composite relationship score from 0 to 100 |
| RelationshipTier | Weak, Developing, Strong, or Very Strong |
| PredictedChurnProbability | Random-forest estimated churn probability |
| PredictedRiskTier | Low, Moderate, High, or Critical |
