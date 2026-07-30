# Project Feedback Video Script

## Recommended duration

5 to 7 minutes.

## 0:00-0:20 - Introduction

Hello, my name is Aniket Chakraborty. This project is titled Customer Engagement and Product Utilization Analytics for Retention Strategy. The purpose of this project is to analyze customer engagement, banking-product usage and relationship strength so that banks can identify customers who may leave and design better retention strategies.

## 0:20-0:50 - Problem statement

Banks have customer information such as balance, salary, credit score and demographic details. However, a high balance does not always mean that the customer has a strong relationship with the bank. A valuable customer may become inactive, use very few products or gradually disengage. This project therefore studies churn from the perspective of customer behaviour, engagement and product utilization.

## 0:50-1:20 - Dataset

The project uses a European bank dataset containing 10,000 customer records. It includes customer ID, credit score, geography, gender, age, tenure, account balance, number of products, credit-card ownership, active-member status, estimated salary and exit status. The Exited column is the target variable, where one means that the customer left and zero means that the customer was retained.

## 1:20-1:50 - Data preparation

I validated the required columns, checked missing values and duplicate customer identifiers, and created additional features such as age bands, activity status, engagement segments, relationship-strength tiers and predicted churn-risk levels.

## 1:50-2:25 - Dashboard filters and KPIs

The dashboard provides dynamic filters for geography, gender, age, tenure, number of products and account balance. Every KPI, chart and customer table updates when a filter changes. The main indicators include customer count, churn rate, retention rate, active-member rate, average products, Engagement Retention Ratio, Product Depth Index, High-Balance Disengagement Rate, Credit-Card Stickiness Score and Relationship Strength Index.

## 2:25-3:00 - Engagement analysis

The engagement analysis shows that activity is one of the strongest operational retention indicators. Active customers have an historical retention rate of approximately 85.73 percent, while inactive customers show much higher churn. Customers are classified into Active Engaged, Active Low-Product, Inactive High-Balance and Inactive Disengaged profiles.

## 3:00-3:35 - Product utilization

Two-product customers show the strongest historical retention. One-product customers have a much higher churn rate. Three- and four-product customers show unusually high churn, but these groups are small, so the result should be investigated for product complexity or poor product fit rather than treated as direct causation.

## 3:35-4:05 - Geography

Germany has the highest historical churn rate at approximately 32.44 percent, substantially higher than France and Spain. This suggests a need for a market-specific diagnostic and retention pilot.

## 4:05-4:40 - Premium customer risk

The Premium Risk module identifies customers in the highest balance quartile and examines whether they are active or disengaged. Inactive premium customers have an historical churn rate of approximately 30.47 percent. The dashboard creates a downloadable priority queue for relationship-manager review.

## 4:40-5:25 - Machine-learning model

A Random Forest model is used as a churn-risk decision-support tool. It uses credit score, geography, age, tenure, balance, number of products, card ownership, activity status and estimated salary. Gender is excluded from operational prediction and is retained only for fairness monitoring. The model achieved an ROC AUC of approximately 0.8545. The simulator allows a user to enter a customer profile and estimate churn probability and risk tier.

## 5:25-5:50 - Customer explorer

The Customer Explorer supports customer-ID or surname search, customer-level review and CSV download. This converts analytical findings into an operational retention workflow.

## 5:50-6:25 - Recommendations

The main recommendations are to prioritize inactive high-balance customers, offer a suitable second product to appropriate one-product customers, investigate the high churn among three- and four-product customers, and conduct a localized retention pilot for Germany. All interventions should be validated using controlled groups.

## 6:25-6:50 - Limitations and conclusion

This analysis uses historical cross-sectional data, so it identifies associations rather than proving causation. Additional transaction, complaint and digital-channel data would improve the analysis. In conclusion, this project transforms customer data into practical retention intelligence and supports evidence-based customer engagement decisions. Thank you for watching.
