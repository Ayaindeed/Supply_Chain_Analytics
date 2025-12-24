# Supply Chain Analytics : Prédiction de Demande et Optimisation d'Inventaire

## Description du Projet

Ce projet implémente une architecture complète de Business Intelligence pour l'analyse et l'optimisation de la chaîne logistique. Il combine les technologies modernes d'ETL, de transformation de données et de Machine Learning pour fournir des insights actionnables sur les performances logistiques.

**Technologies utilisées:**
- **Apache Airflow**: Orchestration du pipeline ETL
- **dbt (data build tool)**: Transformation et modélisation des données SQL
- **PostgreSQL**: Data Warehouse
- **XGBoost**: Machine Learning pour la prédiction de demande et des retards
- **Docker**: Containerisation et déploiement
- **Metabase & Apache Superset**: Business Intelligence et dashboards interactifs

## Qualité, Tests et Gestion des Erreurs

État actuel et prochaines étapes:

- **Data Quality — Implémenté**: validations Python et tests dbt
   - Validations Python: [scripts/validation.py](scripts/validation.py)
   - Tests dbt standards: `not_null`, `unique`, `accepted_values`, `accepted_range`
   - Tests personnalisés: [dbt/tests/test_no_future_dates.sql](dbt/tests/test_no_future_dates.sql), [dbt/tests/test_delivery_days_consistency.sql](dbt/tests/test_delivery_days_consistency.sql)

- **Error Handling — Partiellement implémenté**: robustesse opérationnelle
   - Retries, SLAs et callback de défaillance: [airflow/dags/supply_chain_pipeline.py](airflow/dags/supply_chain_pipeline.py)
   - À ajouter (prochaine étape): alerting externe (Slack/Email) branché sur `notify_failure()`

- **Testing — Implémenté**: couverture unitaire et de transformation
   - Tests unitaires de validation: [tests/test_validation_raw.py](tests/test_validation_raw.py), [tests/test_validation_features.py](tests/test_validation_features.py)
   - Suite de tests dbt (qualité et contraintes) exécutables via `dbt test`
   - Optionnel: script d’intégration end-to-end (extraction → dbt → features → ML)

## Architecture du Système

```
Dataset CSV (Kaggle)
    ↓
[Airflow - Orchestration]
    ├─ Extraction (Python/Pandas)
    ├─ Transformation (dbt/SQL)
    ├─ Tests Qualité (dbt)
    ├─ Feature Engineering (Python)
    └─ ML Modeling (XGBoost)
    ↓
[PostgreSQL - Data Warehouse]
    ├─ raw_data (données brutes)
    ├─ staging (données nettoyées)
    ├─ intermediate (transformations)
    ├─ marts (tables finales)
    └─ analytics (prédictions ML)
    ↓
[Metabase (Port 3000) & Superset (Port 8088)]
    ├─ Interactive Dashboards
    ├─ KPI Monitoring
    └─ Advanced Analytics
```

## Structure du Projet

```
supply_chain_mgmt/
│
├── airflow/
│   └── dags/
│       ├── supply_chain_pipeline.py    # DAG principal
│       └── requirements.txt
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   └── ...                     # Modèles de staging (vues)
│   │   ├── intermediate/
│   │   │   ├── int_delivery_performance.sql
│   │   │   └── int_product_performance.sql
│   │   └── marts/
│   │       ├── fct_supply_chain.sql       # Table de faits (principale)
│   │       ├── fct_supply_chain_v2.sql    # Variante de la table de faits
│   │       ├── dim_customers.sql          # Dimension clients
│   │       ├── dim_date.sql               # Dimension date
│   │       ├── dim_geography.sql          # Dimension géographie
│   │       ├── dim_products.sql           # Dimension produits
│   │       ├── dim_shipping.sql           # Dimension mode livraison
│   │       └── vw_kpi_global.sql          # Vue KPI agrégés
│   ├── tests/
│   │   ├── test_no_future_dates.sql
│   │   └── test_delivery_days_consistency.sql
│   ├── dbt_project.yml                 # Configuration dbt
│   ├── profiles.yml                    # Profils de connexion
│   └── packages.yml                    # Packages dbt
│
├── scripts/
│   ├── extract_data.py                 # Extraction CSV → PostgreSQL
│   ├── feature_engineering.py          # Création de features ML
│   ├── ml_modeling.py                  # Entraînement modèles ML
│   └── init_database.py                # Initialisation DB
│
├── ml_models/                          # Modèles ML sauvegardés
│
├── config/
│   └── init.sql                        # Script d'initialisation DB
│
├── dataset/                            # Données Kaggle
│   ├── DataCoSupplyChainDatasetRefined.csv
│   ├── DescriptionDataCoSupplyChainRefined.csv
│   ├── dest_points.geojson
│   ├── routes.geojson
│   └── src_points.geojson
│
├── notebooks/                          # Notebooks d'analyse
│   └── exploratory_analysis.py
│
├── docker-compose.yml                  # Configuration Docker
├── requirements.txt                    # Dépendances Python
├── .env                                # Variables d'environnement
├── .env.example                        # Template variables
├── docs/                               # Documentation additionnelle
├── .gitignore
└── README.md                           # Ce fichier
```

## Ressources et Documentation

### Documentation Officielle
- [Apache Airflow](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [XGBoost](https://xgboost.readthedocs.io/)
- [Metabase](https://www.metabase.com/docs/)
- [Apache Superset](https://superset.apache.org/docs/)

### Dataset Source
- [Kaggle - DataCo Supply Chain Dataset](https://www.kaggle.com/datasets/aaumgupta/refined-dataco-supply-chain-geospatial-dataset)
