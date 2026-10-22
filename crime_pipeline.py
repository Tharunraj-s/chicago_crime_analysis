"""Leakage-aware incident classification. This does not forecast future crime."""
import argparse
from pathlib import Path


def build_pipeline(mode='numeric', folds=2):
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import StringIndexer, VectorAssembler, Tokenizer, StopWordsRemover, CountVectorizer, IDF
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
    from pyspark.ml.evaluation import MulticlassClassificationEvaluator
    stages = [StringIndexer(inputCol='primary_type', outputCol='label', handleInvalid='keep')]
    inputs = []
    if mode in ('numeric', 'combined'):
        inputs.extend(['year', 'latitude', 'longitude', 'month', 'hour'])
    if mode in ('text', 'combined'):
        stages.extend([Tokenizer(inputCol='description', outputCol='words'),
                       StopWordsRemover(inputCol='words', outputCol='filtered_words'),
                       CountVectorizer(inputCol='filtered_words', outputCol='tf', vocabSize=1000),
                       IDF(inputCol='tf', outputCol='tfidf')])
        inputs.append('tfidf')
    stages.extend([VectorAssembler(inputCols=inputs, outputCol='features', handleInvalid='error'),
                   RandomForestClassifier(labelCol='label', featuresCol='features', seed=42)])
    pipeline = Pipeline(stages=stages)
    rf = stages[-1]
    grid = ParamGridBuilder().addGrid(rf.numTrees, [10, 50]).addGrid(rf.maxDepth, [5, 10]).build()
    return CrossValidator(estimator=pipeline, estimatorParamMaps=grid,
                          evaluator=MulticlassClassificationEvaluator(metricName='f1'),
                          numFolds=folds, seed=42, parallelism=1)


def load_data(spark, path):
    from pyspark.sql import functions as F
    frame = spark.read.option('header', True).option('inferSchema', True).csv(str(path))
    names = [name.strip().lower().replace(' ', '_') for name in frame.columns]
    if len(names) != len(set(names)):
        raise ValueError('Column normalisation produced duplicate names')
    frame = frame.toDF(*names)
    required = {'primary_type', 'year', 'latitude', 'longitude', 'date'}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    # try_to_timestamp returns null for unmatched formats under ANSI mode.
    date = F.coalesce(F.try_to_timestamp('date', F.lit('MM/dd/yyyy hh:mm:ss a')),
                      F.try_to_timestamp('date', F.lit('dd/MM/yyyy HH:mm')),
                      F.try_to_timestamp('date', F.lit('yyyy-MM-dd HH:mm:ss')))
    frame = frame.withColumn('parsed_date', date).withColumn('month', F.month('parsed_date')).withColumn('hour', F.hour('parsed_date'))
    for name in ('year', 'latitude', 'longitude'):
        frame = frame.withColumn(name, F.expr(f'try_cast(`{name}` as double)'))
    if 'description' not in frame.columns:
        frame = frame.withColumn('description', F.lit(''))
    frame = frame.fillna({'description': ''})
    return frame.dropna(subset=['primary_type', 'year', 'latitude', 'longitude', 'month', 'hour'])


def evaluate(predictions, labels):
    from pyspark.ml.evaluation import MulticlassClassificationEvaluator
    from pyspark.sql import functions as F
    metrics = {name: MulticlassClassificationEvaluator(metricName=name).evaluate(predictions)
               for name in ('accuracy', 'weightedPrecision', 'weightedRecall', 'f1')}
    # Full actual/predicted counts; FP must be grouped by predicted class.
    confusion = predictions.groupBy('label', 'prediction').count()
    confusion.show(truncate=False)
    rows = []
    for i, name in enumerate(labels):
        tp = predictions.filter((F.col('label') == i) & (F.col('prediction') == i)).count()
        predicted = predictions.filter(F.col('prediction') == i).count()
        actual = predictions.filter(F.col('label') == i).count()
        precision = tp / predicted if predicted else 0.0
        recall = tp / actual if actual else 0.0
        rows.append((name, precision, recall, 2 * precision * recall / (precision + recall) if precision + recall else 0.0))
    return metrics, rows


def run(path, mode='numeric', folds=2):
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName('ChicagoIncidentClassification').getOrCreate()
    try:
        frame = load_data(spark, path)
        if frame.count() < 20:
            raise ValueError('Too few valid records after schema/date cleaning')
        train, test = frame.randomSplit([0.8, 0.2], seed=42)
        train = train.cache()
        test = test.cache()
        if not train.count() or not test.count():
            raise ValueError('Train/test split is empty')
        fitted = build_pipeline(mode, folds).fit(train)
        predictions = fitted.transform(test).cache()
        labels = fitted.bestModel.stages[0].labels
        metrics, classes = evaluate(predictions, labels)
        print(metrics)
        for row in classes:
            print(row)
        return metrics, classes
    finally:
        spark.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--mode', choices=['numeric', 'text', 'combined'], default='numeric',
                        help='Text modes are retrospective and may encode the target category')
    parser.add_argument('--folds', type=int, default=2)
    args = parser.parse_args()
    if args.folds < 2:
        parser.error('--folds must be at least 2')
    run(args.csv, args.mode, args.folds)
