# Supply Chain Analytics : Prédiction de Demande et Optimisation d'Inventaire

## Description du Projet

Ce projet implémente une architecture complète de Business Intelligence pour l'analyse et l'optimisation de la chaîne logistique. Il combine les technologies modernes d'ETL, de transformation de données et de Machine Learning pour fournir des insights actionnables sur les performances logistiques, incluant des prédictions de demande et de risques de retard exposées dans des dashboards dédiés.

**Technologies utilisées:**
- **Apache Airflow**: Orchestration du pipeline ETL
- **dbt (data build tool)**: Transformation et modélisation des données SQL
- **PostgreSQL**: Data Warehouse
- **Python + XGBoost**: Machine Learning pour la prédiction de demande et des retards
- **Docker**: Containerisation et déploiement
- **Power BI**: Business Intelligence et dashboards interactifs (visualisations avancées, DAX)

## Qualité, Tests et Gestion des Erreurs

État actuel et prochaines étapes:
- **Data Quality — Implémenté**: validations Python et tests dbt
   - Validations Python: [scripts/validation.py](scripts/validation.py)
   - Tests dbt standards: `not_null`, `unique`, `accepted_values`, `accepted_range`
   - Tests personnalisés: [dbt/tests/test_no_future_dates.sql](dbt/tests/test_no_future_dates.sql), [dbt/tests/test_delivery_days_consistency.sql](dbt/tests/test_delivery_days_consistency.sql), [dbt/tests/test_ml_predictions_not_empty.sql](dbt/tests/test_ml_predictions_not_empty.sql)

- **ML Predictions — Implémenté**: Exposition des prédictions dans analytics + dashboards dédiés
  - Modèles dbt: [dbt/models/analytics/](dbt/models/analytics/)
  - Dashboards Power BI: [POWER_BI_ADVANCED_VISUALS_GUIDE.md](POWER_BI_ADVANCED_VISUALS_GUIDE.md) et [docs/presentation_fr.md](docs/presentation_fr.md)
- **Error Handling —  implémenté**: robustesse opérationnelle
   - Retries, SLAs et callback de défaillance: [airflow/dags/supply_chain_pipeline.py](airflow/dags/supply_chain_pipeline.py)


## Architecture du Système

```
Dataset CSV (Kaggle)
  ↓
Airflow (orchestration)
  ├─ Extraction (Python/Pandas)
  ├─ Transformation (dbt/SQL)
  ├─ Tests Qualité (dbt)
  ├─ Feature Engineering (Python)
  └─ ML Modeling (XGBoost) → export prédictions
  ↓
PostgreSQL (Data Warehouse)
  ├─ raw_data
  ├─ staging
  ├─ intermediate
  ├─ marts
  └─ analytics (prédictions ML + métriques)
  ↓
Power BI (dashboards)
  ├─ Page 1: Vue exécutive (KPIs, ventes, risques)
  ├─ Page 2: Performance livraison & SLA
  ├─ Page 3: Analytique ML (accuracy, confusion matrix, trends)
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
│   │   ├── sources.yml                 # Définition des sources externes
│   │   ├── staging/
│   │   │   └── ...                     # Modèles de staging (vues)
│   │   ├── intermediate/
│   │   │   ├── int_delivery_performance.sql
│   │   │   └── int_product_performance.sql
│   │   ├── marts/
│   │   │   ├── fct_supply_chain.sql       # Table de faits (principale)
│   │   │   ├── fct_supply_chain_v2.sql    # Variante de la table de faits
│   │   │   ├── dim_customers.sql          # Dimension clients
│   │   │   ├── dim_date.sql               # Dimension date
│   │   │   ├── dim_geography.sql          # Dimension géographie
│   │   │   ├── dim_products.sql           # Dimension produits
│   │   │   ├── dim_shipping.sql           # Dimension mode livraison
│   │   │   └── vw_kpi_global.sql          # Vue KPI agrégés
│   │   └── analytics/
│   │       ├── ml_predictions.sql         # Vue sur prédictions ML
│   │       └── ml_model_metrics.sql       # Vue sur métriques modèles
│   ├── tests/
│   │   ├── test_no_future_dates.sql
│   │   ├── test_delivery_days_consistency.sql
│   │   └── test_ml_predictions_not_empty.sql  # Test données ML
│   ├── dbt_project.yml                 # Configuration dbt
│   ├── profiles.yml                    # Profils de connexion
│   └── packages.yml                    # Packages dbt
│
├── scripts/
│   ├── extract_data.py                 # Extraction CSV → PostgreSQL
│   ├── eda_analysis.py                 # Analyse exploratoire des données
│   ├── feature_engineering.py          # Création de features ML
│   ├── ml_modeling.py                  # Entraînement modèles ML
│   └── init_database.py                # Initialisation DB
│
├── ml_models/                          # Modèles ML sauvegardés
│
├── config/
│   ├── init.sql                        # Script d'initialisation DB
│   └── saiku-schema.xml                # Schéma OLAP pour Saiku
│
├── dataset/                            # Données Kaggle
│   ├── DataCoSupplyChainDatasetRefined.csv
│   ├── DescriptionDataCoSupplyChainRefined.csv
│   ├── dest_points.geojson              # Points de destination (géospatial)
│   ├── routes.geojson                   # Routes logistiques (géospatial)
│   └── src_points.geojson               # Points source (géospatial)
│
├── notebooks/                          # Notebooks d'analyse
│   └── exploratory_analysis.py
│
├── docker-compose.yml                  # Configuration Docker
├── requirements.txt                    # Dépendances Python
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
- [Power BI](https://learn.microsoft.com/power-bi/)

### Dataset Source
- [Kaggle - DataCo Supply Chain Dataset](https://www.kaggle.com/datasets/aaumgupta/refined-dataco-supply-chain-geospatial-dataset)