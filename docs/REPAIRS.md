# Corrected modelling entry point

```bash
python crime_pipeline.py /path/to/crimes.csv --mode numeric
```

Use PySpark 3.5 with a compatible Java runtime. Input column spaces are normalised to underscores. The loader handles the source Chicago timestamp format and the previously used cleaned formats. Invalid essential records are dropped; no learned preprocessing is fitted before splitting.

`numeric` uses time and location attributes. `text` and `combined` are explicitly retrospective experiments because description can encode crime category. Arrest is excluded. These models do not forecast future crime.

Cross-validation wraps the entire label/feature/estimator pipeline. Features stay on the same dataframe; there are no independently generated partition-dependent join IDs. Label names come from the fitted training pipeline. Class precision uses predicted counts, recall uses actual counts, and the confusion table retains all actual/predicted pairs.

modelling.ipynb and feature_analysis.ipynb now call this module. Original versions and outputs are preserved under archive/; old scores are not claimed for the corrected code.

Validation: syntax and notebook structure checked. No Spark runtime or source CSV is available in this workspace; a dataset-backed training run is still required. Cleaning/EDA notebook outputs remain historical artifacts, not newly validated results.
