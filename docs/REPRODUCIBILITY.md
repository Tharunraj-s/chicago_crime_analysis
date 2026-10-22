# Reproduction review

feature_analysis.ipynb and modelling.ipynb code were inspected. Large cleaning/EDA notebooks and the PDF/DBC were inventoried but not fully reviewed. No Spark job was executed.

## Run preparation
- Restore the original data source, extract version, cleaning settings and expected schema.
- Replace the Colab-specific input path in feature_analysis.ipynb and part.csv in modelling.ipynb.
- Reconcile column names and timestamp formats across notebook stages.
- modelling.ipynb requests 8 GB driver memory; provision an appropriate Spark environment.

## Evaluation issues observed
- Feature-analysis scalers, vocabulary, IDF and label encoders are fitted before the split. Fit learned preprocessing on training data to avoid leakage.
- Feature analysis separately assigns monotonically_increasing_id to multiple transformed frames and joins on that ID. Such IDs are partition-dependent; preserve a stable source ID or construct features within one frame.
- Incident descriptions may encode the target crime category. Arrest is also an incident/outcome attribute. Interpret results as retrospective classification unless an explicit prediction-time feature policy is established.
- The final per-class precision calculation groups mismatches by actual class and counts each as both FP and FN. That does not compute per-class precision correctly.
- Label names are reconstructed by fitting a new indexer on the full dataset; extract the fitted training pipeline's label mapping instead.
- The estimator-only cross-validation stage follows already-fitted preprocessing. Use a complete preprocessing-and-estimator pipeline within cross-validation when assessing that pipeline.

Historical notebooks are preserved. No metrics were recalculated and no predictive-validity claim has been verified.
