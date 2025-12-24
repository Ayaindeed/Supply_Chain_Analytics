"""
DAG Airflow pour le pipeline ETL de Supply Chain Analytics
Architecture: Extraction -> dbt Transform -> Feature Engineering -> ML Modeling
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os
import logging

# Ajouter le répertoire scripts au path
sys.path.insert(0, '/opt/airflow/scripts')

from extract_data import extract_csv_to_postgres
from feature_engineering import create_features
from ml_modeling import train_demand_prediction_model

logger = logging.getLogger(__name__)


def notify_failure(context):
    """Generic on-failure callback for Airflow tasks.
    Logs useful context to ease troubleshooting. Can be extended to send webhooks.
    """
    task_instance = context.get('task_instance')
    exception = context.get('exception')
    dag_id = context.get('dag').dag_id if context.get('dag') else 'unknown_dag'
    run_id = context.get('run_id', 'unknown_run')
    logger.error(
        "Task failure: dag=%s task=%s run_id=%s error=%s",
        dag_id,
        getattr(task_instance, 'task_id', 'unknown_task'),
        run_id,
        repr(exception),
    )

# Configuration par défaut du DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
dag = DAG(
    'supply_chain_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL complet pour l\'analyse de la chaîne logistique',
    schedule_interval='0 2 * * *',  # Tous les jours à 2h du matin
    catchup=False,
    tags=['supply_chain', 'etl', 'dbt', 'ml'],
)

# ===== TASK 1: EXTRACTION DES DONNÉES =====
task_extract = PythonOperator(
    task_id='extract_csv_to_postgres',
    python_callable=extract_csv_to_postgres,
    on_failure_callback=notify_failure,
    sla=timedelta(minutes=30),
    dag=dag,
    doc_md="""
    ### Extraction des données
    - Lit le fichier CSV DataCoSupplyChainDatasetRefined.csv
    - Charge les données dans PostgreSQL (schéma: raw_data)
    - Retourne le nombre de lignes chargées
    """
)

# ===== TASK 2: DBT - TRANSFORMATION =====
task_dbt_deps = BashOperator(
    task_id='dbt_install_dependencies',
    bash_command='cd /opt/airflow/dbt && rm -rf dbt_packages && dbt deps --profiles-dir .',
    on_failure_callback=notify_failure,
    dag=dag,
    doc_md="Installer les dépendances dbt (packages) - supprime et réinstalle pour éviter les erreurs de permission"
)

task_dbt_run = BashOperator(
    task_id='dbt_run_models',
    bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    on_failure_callback=notify_failure,
    sla=timedelta(minutes=45),
    dag=dag,
    doc_md="""
    ### Transformation dbt
    - Exécute tous les modèles dbt
    - Crée les vues staging, intermediate et tables marts
    - Ordre d'exécution géré automatiquement par dbt
    """
)

# ===== TASK 3: DBT - TESTS DE QUALITÉ =====
task_dbt_test = BashOperator(
    task_id='dbt_test_data_quality',
    bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
    on_failure_callback=notify_failure,
    sla=timedelta(minutes=20),
    dag=dag,
    doc_md="""
    ### Tests de qualité des données
    - Vérifie l'unicité des clés primaires
    - Valide les valeurs acceptées
    - Teste les contraintes métier
    """
)

# ===== TASK 4: FEATURE ENGINEERING =====
task_features = PythonOperator(
    task_id='create_ml_features',
    python_callable=create_features,
    on_failure_callback=notify_failure,
    sla=timedelta(minutes=20),
    dag=dag,
    doc_md="""
    ### Feature Engineering
    - Crée des features pour le Machine Learning
    - Calcule des métriques dérivées
    - Sauvegarde dans la table features_ml
    """
)

# ===== TASK 5: MACHINE LEARNING =====
task_ml_model = PythonOperator(
    task_id='train_demand_prediction',
    python_callable=train_demand_prediction_model,
    on_failure_callback=notify_failure,
    sla=timedelta(minutes=30),
    dag=dag,
    doc_md="""
    ### Entraînement du modèle ML
    - Entraîne un modèle XGBoost pour prédire la demande
    - Évalue la performance (R², MAE, RMSE)
    - Sauvegarde le modèle et les prédictions
    """
)

# ===== TASK 6: GÉNÉRATION DE LA DOCUMENTATION DBT =====
task_dbt_docs = BashOperator(
    task_id='dbt_generate_docs',
    bash_command='cd /opt/airflow/dbt && dbt docs generate --profiles-dir .',
    on_failure_callback=notify_failure,
    dag=dag,
    doc_md="Génère la documentation dbt interactive"
)

# ===== DÉFINITION DES DÉPENDANCES =====
# Pipeline linéaire avec embranchement pour la documentation
task_extract >> task_dbt_deps >> task_dbt_run >> task_dbt_test >> task_features >> task_ml_model
task_dbt_run >> task_dbt_docs
