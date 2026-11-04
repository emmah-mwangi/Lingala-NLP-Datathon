"""
nlp — Team 07 (Datalynk) application package.

Public surface
--------------
    from nlp.config      import model_path, SUPPORTED_TRACKS, ...
    from nlp.data_loader import load_model_pack, load_dev_metrics, ...
    from nlp.predictor   import predict, PredictionResult
    from nlp.utils       import normalise_text, format_probability

Integration dependencies
------------------------
The following artefacts are produced by Tatyana's pipeline scripts and
must exist before the prediction path is reachable:

    artifacts/<track>/model.joblib      — created by train.py
    artifacts/<track>/dev_metrics.json  — created by train.py
    artifacts/<track>/test_metrics.json — created by evaluate.py
    artifacts/<track>/test_predictions.csv — created by evaluate.py

The data_loader module raises ModelNotTrainedError with a clear message
when these files are absent, so the application degrades gracefully.
"""
