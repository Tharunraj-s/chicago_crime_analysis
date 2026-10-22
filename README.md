# Chicago Crime Analysis with Apache Spark

Group coursework exploring Chicago crime records through cleaning, exploratory analysis, feature engineering and Spark MLlib classification.

## Notebook sequence

| Step | File |
|---|---|
| 1. Cleaning | [cleaning.ipynb](cleaning.ipynb) |
| 2. Exploratory analysis | [eda.ipynb](eda.ipynb) |
| 3. Feature comparison | [feature_analysis.ipynb](feature_analysis.ipynb) |
| 4. Random Forest modelling | [modelling.ipynb](modelling.ipynb) |

[Group report](Project_Group_21_report.pdf) · [Databricks archive](Group_Rory/Group_Rory/chicago_clean.dbc) · [Inventory](docs/INVENTORY.md) · [Reproduction review](docs/REPRODUCIBILITY.md)

## Setup

Use a Spark/Databricks environment or a compatible local Java/PySpark installation. requirements.txt lists candidate Python dependencies; no original environment lock was uploaded.

The crime CSV is not included. Obtain the source dataset and set paths in each notebook. modelling.ipynb expects part.csv; feature_analysis.ipynb references a Colab-specific CSV path. The two notebooks also expect different column naming conventions (spaces versus underscores).

## Modelling scope

modelling.ipynb predicts the recorded crime category using incident attributes with a Random Forest pipeline and cross-validation. It includes description and arrest-related fields: this is incident classification, not demonstrated prediction of future crimes.

Saved outputs and the report are historical experiment evidence. No performance number is presented here as independently reproduced.

Original notebook paths are preserved because working-directory and schema assumptions need to be reconciled before refactoring.
