"""
Script de Feature Engineering pour le Machine Learning
Crée des features avancées à partir des données transformées par dbt
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import List

from validation import validate_features_dataframe

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()


def get_db_connection():
    """Créer une connexion à la base de données PostgreSQL"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'supply_chain_dw')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(connection_string)


def create_staging_schema(engine):
    """Créer le schéma staging s'il n'existe pas"""
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        logger.info("Schéma staging créé ou déjà existant")
    except Exception as e:
        logger.error(f"Erreur lors de la création du schéma staging: {e}")
        raise


def create_features():
    """
    Créer des features pour le Machine Learning
    """
    try:
        engine = get_db_connection()
        create_staging_schema(engine)
        
        # Lire les données depuis la table de faits dbt
        logger.info("Lecture des données depuis analytics_marts.fct_supply_chain...")
        query = """
        SELECT 
            order_id,
            order_item_id,
            order_date,
            customer_id,
            order_year,
            order_month,
            order_quarter,
            order_day,
            days_for_shipping_real,
            days_for_shipment_scheduled,
            shipping_delay_days,
            late_delivery_risk,
            delivery_status,
            order_region,
            order_country,
            market,
            sales,
            order_profit_per_order,
            benefit_per_order,
            is_on_time,
            is_profitable,
            performance_score
        FROM analytics_marts.fct_supply_chain
        """
        
        df = pd.read_sql(query, engine)
        logger.info(f"Données chargées: {len(df)} lignes")
        
        # ===== FEATURE ENGINEERING =====
        
        # 1. Features temporelles avancées
        df['is_weekend'] = df['order_date'].apply(
            lambda x: 1 if pd.to_datetime(x).dayofweek >= 5 else 0
        )
        
        df['days_since_year_start'] = df['order_date'].apply(
            lambda x: pd.to_datetime(x).timetuple().tm_yday
        )
        
        df['is_end_of_month'] = df['order_date'].apply(
            lambda x: 1 if pd.to_datetime(x).day > 25 else 0
        )
        
        df['is_beginning_of_month'] = df['order_date'].apply(
            lambda x: 1 if pd.to_datetime(x).day <= 5 else 0
        )
        
        # 2. Features financières dérivées
        df['revenue_per_shipping_day'] = df['sales'] / (df['days_for_shipping_real'] + 1)
        df['profit_margin'] = (df['order_profit_per_order'] / df['sales'].replace(0, np.nan)) * 100
        df['profit_margin'] = df['profit_margin'].fillna(0)
        
        # 3. Features de catégorisation
        df['is_high_value_order'] = (df['sales'] > df['sales'].quantile(0.75)).astype(int)
        df['is_low_value_order'] = (df['sales'] < df['sales'].quantile(0.25)).astype(int)
        
        df['is_highly_profitable'] = (
            df['order_profit_per_order'] > df['order_profit_per_order'].quantile(0.75)
        ).astype(int)
        
        # 4. Features de délai
        df['delay_vs_scheduled'] = df['shipping_delay_days'] / (df['days_for_shipment_scheduled'] + 1)
        df['is_severe_delay'] = (df['shipping_delay_days'] > 7).astype(int)
        
        # 5. Encodage des variables catégorielles
        df['delivery_status_encoded'] = pd.factorize(df['delivery_status'])[0]
        df['market_encoded'] = pd.factorize(df['market'])[0]
        df['order_region_encoded'] = pd.factorize(df['order_region'])[0]
        df['performance_score_encoded'] = pd.factorize(df['performance_score'])[0]
        
        # 6. Features d'agrégation par client
        customer_stats = df.groupby('customer_id').agg({
            'order_id': 'count',
            'sales': ['sum', 'mean'],
            'late_delivery_risk': 'mean'
        }).reset_index()
        
        customer_stats.columns = [
            'customer_id', 
            'customer_total_orders',
            'customer_total_sales',
            'customer_avg_order_value',
            'customer_late_delivery_rate'
        ]
        
        df = df.merge(customer_stats, on='customer_id', how='left')
        
        # 7. Features d'agrégation par région
        region_stats = df.groupby('order_region').agg({
            'late_delivery_risk': 'mean',
            'sales': 'mean'
        }).reset_index()
        
        region_stats.columns = [
            'order_region',
            'region_late_delivery_rate',
            'region_avg_sales'
        ]
        
        df = df.merge(region_stats, on='order_region', how='left')
        
        # 8. Interaction features
        df['high_value_late_risk'] = df['is_high_value_order'] * df['late_delivery_risk']
        df['market_season_interaction'] = df['market_encoded'] * df['order_quarter']
        
        logger.info(f"Features créées: {len(df.columns)} colonnes au total")

        # Validation des features requises (pour usage ML ultérieur)
        required_for_ml: List[str] = [
            'order_month', 'order_quarter', 'order_day', 'order_year',
            'days_for_shipment_scheduled', 'is_weekend', 'days_since_year_start',
            'is_end_of_month', 'is_beginning_of_month', 'market_encoded',
            'order_region_encoded', 'customer_total_orders', 'customer_avg_order_value',
            'region_avg_sales', 'customer_late_delivery_rate', 'region_late_delivery_rate',
            'is_high_value_order', 'profit_margin'
        ]
        validate_features_dataframe(df, required_for_ml)
        
        # Sauvegarder dans PostgreSQL
        table_name = 'features_ml'
        logger.info(f"Sauvegarde des features dans staging.{table_name}...")
        
        df.to_sql(
            table_name,
            engine,
            schema='staging',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        logger.info(f"Features sauvegardées avec succès: {len(df)} lignes")
        
        # Statistiques
        logger.info(f"Nombre de features: {len(df.columns)}")
        logger.info(f"Features numériques: {df.select_dtypes(include=[np.number]).shape[1]}")
        logger.info(f"Features catégorielles: {df.select_dtypes(include=['object']).shape[1]}")
        
        return f"Feature Engineering réussi: {len(df)} lignes, {len(df.columns)} colonnes"
        
    except Exception as e:
        logger.exception(f"Erreur lors du feature engineering: {e}")
        raise


if __name__ == "__main__":
    result = create_features()
    print(result)
