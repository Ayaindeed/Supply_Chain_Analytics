# Scripts d'Initialisation Python

Ce dossier contient tous les scripts Python nécessaires pour le pipeline ETL:

## Scripts Disponibles

### 1. extract_data.py
Extraction des données CSV vers PostgreSQL
- Lit le fichier DataCoSupplyChainDatasetRefined.csv
- Charge les données dans le schéma raw_data
- Gère l'encodage et les erreurs

### 2. feature_engineering.py
Création des features pour le Machine Learning
- Lit depuis marts.fct_supply_chain
- Crée des features temporelles, financières, catégorielles
- Sauvegarde dans staging.features_ml

### 3. ml_modeling.py
Entraînement des modèles Machine Learning
- Modèle de régression: prédiction de la demande
- Modèle de classification: risque de retard
- Sauvegarde les modèles et les prédictions

### 4. init_database.py
Initialisation de la base de données
- Crée tous les schémas nécessaires
- Utile pour le setup initial

## Utilisation

Chaque script peut être exécuté indépendamment:

```bash
python scripts/extract_data.py
python scripts/feature_engineering.py
python scripts/ml_modeling.py
python scripts/init_database.py
```

Ou via Airflow qui orchestre leur exécution.
