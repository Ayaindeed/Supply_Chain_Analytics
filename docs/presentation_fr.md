# Présentation du Projet — Supply Chain Analytics

## 1. Problématique & Enjeux
- Variabilité de la demande et retards de livraison impactent le coût et la satisfaction client.
- Manque de traçabilité bout‑en‑bout des transformations et de la qualité des données.
- Besoin de KPIs fiables et de prédictions pour anticiper la demande et les risques logistiques.
- Contexte: Supply chain globale avec données multi-sources (ventes, logistique, clients).
- Impact: Réduction des coûts opérationnels et amélioration de la visibilité en temps réel.

## 1.1. Valeur Métier & ROI
- **Réduction des coûts**: Optimisation des stocks (-15-20% de surstock), réduction des retards (-25% de pénalités).
- **Amélioration du service client**: Augmentation du taux de livraison à temps (+30%), satisfaction client mesurée.
- **ROI estimé**: Retour sur investissement en 6-12 mois via économies opérationnelles.
- **Métriques clés**: NPV (valeur actuelle nette), payback period, impact sur la marge brute.

## 2. Objectifs (Pourquoi nous faisons cela)
- Orchestrer un pipeline ETL reproductible et observable (Airflow).
- Normaliser et tester les transformations SQL (dbt) pour un DW propre.
- Exposer des insights rapides via BI (Metabase, Superset) et des modèles ML (XGBoost).
- Réduire le temps d’analyse et améliorer la prise de décision opérationnelle.
- Livrables: DW avec schémas star, modèles ML déployés, dashboards interactifs.

## 3. Dataset (Vue d’ensemble)
- Source: Kaggle “Refined DataCo Supply Chain Geospatial Dataset”.
- Données tabulaires + géospatiales (CSV + GeoJSON):
  - Commandes: `order_id`, `order_date_dateorders`, `order_status`, `sales`, `order_profit_per_order`, `order_item_quantity`, etc.
  - Livraison: `days_for_shipping_real`, `days_for_shipment_scheduled`, `delivery_status`, `late_delivery_risk`.
  - Client & géographie: `customer_id`, `customer_segment`, `order_region`, `order_country`, `market`.
  - Géospatial: `latitude_src/longitude_src`, `latitude_dest/longitude_dest`, `routes.geojson`, `src_points.geojson`, `dest_points.geojson`.
- Description des champs: voir [dataset/DescriptionDataCoSupplyChainRefined.csv](../dataset/DescriptionDataCoSupplyChainRefined.csv).
- Volume: ~180k lignes, 53 colonnes, période 2015-2018.
- Qualité: Données nettoyées, mais nécessite validation (dates futures, valeurs manquantes).

## 4. Data Warehouse (Schéma logique)
- Schémas PostgreSQL:
  - `raw_data`: données brutes chargées depuis le CSV.
  - `staging`: vues nettoyées + table `features_ml` pour le ML.
  - `intermediate`: transformations intermédiaires (ex. `int_delivery_performance.sql`).
  - `marts`: tables finales analytiques (faits & dimensions) et vues KPI.
  - `analytics`: réservé aux sorties ML.
- Principales tables (marts):
  - Faits: `fct_supply_chain`, `fct_supply_chain_v2`.
  - Dimensions: `dim_customers`, `dim_date`, `dim_geography`, `dim_products`, `dim_shipping`.
  - KPIs: `vw_kpi_global`.
- Architecture: Schéma en étoile pour optimiser les requêtes BI/ML.

## 5. Pipeline (Airflow DAG)
- Tâches clés (voir [airflow/dags/supply_chain_pipeline.py](../airflow/dags/supply_chain_pipeline.py)):
  1. Extraction CSV → PostgreSQL (`raw_data.supply_chain_raw`).
  2. `dbt deps` puis `dbt run` (staging/intermediate/marts).
  3. `dbt test` (qualité: not_null/unique/accepted_values/range + custom).
  4. Feature engineering (crée `staging.features_ml`).
  5. Modélisation ML (régression demande + classification retard, XGBoost).
  6. `dbt docs generate` (documentation des modèles).
- Dépendances: Linéaire avec branche pour docs; retries et SLAs configurés.
- Observabilité: Logs, callbacks d'erreur, alerting TODO.

## 6. Pourquoi ces choix techniques
- Airflow: orchestration, retries, SLAs, logs et dépendances explicites.
- dbt: transformations SQL versionnées, dépendances automatiques (`ref`), tests intégrés, docs.
- PostgreSQL: DW robuste, SQL riche, intégration BI/ML simple.
- Docker: environnement reproductible, démarrage en une commande.
- Metabase & Superset: BI rapide (Metabase) et analytique avancée (Superset).
- XGBoost: performances excellentes en régression/classification tabulaires.
- Justification: Écosystème mature, open-source, scalable pour PME.

## 6.1. Architecture Technique
```
[Sources de Données]
    ↓
[Ingestion - Airflow + Python]
    ↓
[Stockage - PostgreSQL]
    ├─ Raw Data Layer
    ├─ Staging Layer (dbt)
    ├─ Intermediate Layer
    ├─ Marts Layer (Star Schema)
    └─ Analytics Layer (ML Predictions)
    ↓
[Consommation]
    ├─ BI Tools (Metabase/Superset)
    ├─ ML Models (XGBoost)
    └─ APIs/Exports
```
- **Modularité**: Séparation des couches pour maintenance et évolutivité.
- **Observabilité**: Logs, métriques et alerting intégrés.
- **Sécurité**: Accès contrôlé, chiffrement des données sensibles.

## 7. Tech Stack
- Orchestration: Apache Airflow 2.7.3.
- Transformations: dbt-core 1.7 / dbt-postgres 1.7.
- Data: PostgreSQL 15, SQLAlchemy.
- Python: pandas, numpy, dotenv, pyyaml.
- ML: scikit-learn 1.3, xgboost 2.0.
- BI: Metabase (3000), Apache Superset (8088).
- Conteneurs: Docker Compose (voir [docker-compose.yml](../docker-compose.yml)).
- Autres: pytest pour tests, matplotlib/seaborn pour EDA.

## 7.1. Sécurité & Conformité
- **Authentification**: Utilisation de secrets (dotenv), accès DB via variables d'environnement.
- **Chiffrement**: Données sensibles chiffrées en transit (SSL) et au repos.
- **Conformité**: Respect des standards RGPD pour données clients, audit trails sur modifications.
- **Accès**: Rôles et permissions granulaires dans PostgreSQL et BI tools.
- **Monitoring sécurité**: Logs d'accès, détection d'anomalies.

## 8. Résultats & KPIs (exemples)
- KPI opérationnels (via `marts`):
  - Taux de livraison à temps (`is_on_time`).
  - Taux de commandes profitables (`is_profitable`).
  - Revenu total, valeur moyenne par commande, marge (`order_profit_per_order`).
  - Tendances mensuelles (année/mois depuis `fct_supply_chain`).
- Modèles ML (voir [scripts/ml_modeling.py](../scripts/ml_modeling.py)):
  - Régression (demande/valeur): R², MAE, RMSE, MAPE; importances de features.
  - Classification (risque de retard): accuracy, precision, recall, F1, ROC‑AUC.
- Dashboards Superset/Metabase: revenue par mois, performance régionale, modes d’expédition, segments clients, catégories produits, risque de retard.
- Métriques ML: Modèles entraînés avec validation croisée, sauvegarde des prédictions.
- Exposition des prédictions ML dans `analytics` + dashboards dédiés.

## 9. Mise en œuvre & Développement
- Structure du projet: Scripts Python, DAG Airflow, modèles dbt, tests.
- Développement itératif: Extraction → Validation → Transformation → ML → BI.
- Intégration: Docker pour isolation, git pour versioning.
- Scripts clés: [scripts/extract_data.py](../scripts/extract_data.py), [scripts/feature_engineering.py](../scripts/feature_engineering.py), [scripts/ml_modeling.py](../scripts/ml_modeling.py).
- Durée: ~2-3 semaines pour implémentation complète.

## 10. Défis & Solutions
- Défis: Qualité des données (dates invalides), performance ML (features engineering), intégration BI géospatiale.
- Solutions: Tests dbt custom, validation Python, ajout EDA pour insights, TODO alerting.
- Limitations: Pas d'incrémental pour l'instant, alerting manuel.
- Leçons apprises: Importance de l'EDA précoce, tests automatisés.

## 11. Qualité des données & Tests
- Validations Python: [scripts/validation.py](../scripts/validation.py).
- Tests dbt:
  - Standards: `not_null`, `unique`, `accepted_values`, `accepted_range`.
  - Custom: [dbt/tests/test_no_future_dates.sql](../dbt/tests/test_delivery_days_consistency.sql), [dbt/tests/test_delivery_days_consistency.sql](../dbt/tests/test_delivery_days_consistency.sql).
- Tests unitaires: [tests/test_validation_raw.py](../tests/test_validation_raw.py), [tests/test_validation_features.py](../tests/test_validation_features.py).
- Couverture: Tests sur clés, dates, valeurs métier.

## 12. Déploiement & Exécution
- Démarrage:
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l’état
docker-compose ps
```
- Accès:
  - Airflow: http://localhost:8080 (admin/admin)
  - Metabase: http://localhost:3000
  - Superset: http://localhost:8088 (admin/admin)
  - pgAdmin: http://localhost:5050 (admin@admin.com / admin)
- Connexion DB (Superset/Metabase): `postgresql://postgres:postgres@postgres:5432/supply_chain_dw`.
- Exécution: Lancer le DAG manuellement ou scheduled.

## 12.1. Performance & Monitoring
- **Métriques système**: Temps d'exécution des tâches (<30 min), utilisation CPU/mémoire.
- **Observabilité**: Dashboards Airflow pour suivi des pipelines, alertes sur échecs.
- **Scalabilité**: Architecture containerisée permet montée en charge horizontale.
- **Maintenance**: Backups automatiques, health checks des services.

## 13. Roadmap (prochaines améliorations)
- Alerting Slack/Email sur échec de tâches (brancher `notify_failure`).
- Matérialisation incrémentale pour les grosses tables (dbt).
- Indexation/partitionnement PostgreSQL sur colonnes de jointure/date.
- Monitoring & métriques (Grafana/Prometheus optionnel).
- Intégration géospatiale complète dans Superset (cartes avec GeoJSON).

## 14. Conclusion
- **Réalisations**: Pipeline ETL/ML complet, DW opérationnel, dashboards interactifs, modèles prédictifs déployés.
- **Impact**: Amélioration de la visibilité supply chain, réduction des risques, optimisation des décisions.
- **Leçons clés**: Importance de la qualité des données, modularité technique, tests automatisés.
- **Perspectives**: Extension à d'autres sources de données, intégration temps réel, déploiement en production.
- **Prochaine étape**: Validation métier et mise en production pilote.
