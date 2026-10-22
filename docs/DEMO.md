# Demonstration guide

## Show the project without running a full Spark job
1. Open the submitted report and establish the group-project context.
2. Show original data cleaning and saved EDA.
3. Compare numeric, text and combined feature approaches.
4. Explain the Random Forest pipeline and cross-validation.
5. Open crime_pipeline.py to show the maintained implementation.
6. Distinguish incident classification from future-crime forecasting.

Use report/notebook outputs as evidence of the coursework. Static saved outputs are not live execution; historical scores have not been regenerated after the modelling repairs.

## Local execution
```bash
python crime_pipeline.py /path/to/crimes.csv --mode numeric
```

Requires the source CSV and Spark/Java environment. Text modes may encode the recorded incident category. Add an individual contribution statement later based on the actual division of group work.
