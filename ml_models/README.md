# Modèles Machine Learning

Ce dossier contient les modèles entraînés sauvegardés en format pickle (.pkl).

## Modèles Générés

Après l'exécution de `ml_modeling.py`, vous trouverez:

### 1. demand_prediction_model.pkl
- Type: XGBoost Regressor
- Objectif: Prédire les ventes futures
- Features: métriques temporelles, géographiques, client
- Métrique: R² Score

### 2. late_delivery_risk_model.pkl
- Type: XGBoost Classifier
- Objectif: Prédire le risque de retard de livraison
- Features: délais, région, statut, client
- Métrique: Accuracy, F1-Score

## Utilisation

### Charger un Modèle

```python
import pickle

# Charger le modèle de prédiction de demande
with open('ml_models/demand_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Faire une prédiction
prediction = model.predict(X_new)
```

### Réentraîner

Les modèles sont réentraînés automatiquement à chaque exécution du pipeline.
Pour forcer un réentraînement:

```bash
python scripts/ml_modeling.py
```

## Versioning

Pour versionner les modèles:
1. Ajouter un timestamp au nom du fichier
2. Utiliser MLflow pour le tracking (optionnel)
3. Sauvegarder les métriques dans `analytics.ml_model_metrics`

## Note

Les fichiers .pkl ne sont pas versionnés par défaut dans Git (voir .gitignore).
Pour les versionner, décommenter la ligne dans .gitignore.
