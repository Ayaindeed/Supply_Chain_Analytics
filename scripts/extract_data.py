"""
Script d'extraction des données CSV vers PostgreSQL
Partie du pipeline ETL de Supply Chain Analytics
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging
from typing import Tuple

from validation import validate_raw_dataframe

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def get_db_connection():
    """
    Créer une connexion à la base de données PostgreSQL
    """
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'supply_chain_dw')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    engine = create_engine(connection_string)
    return engine


def create_raw_schema(engine):
    """
    Créer le schéma raw_data s'il n'existe pas
    """
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw_data"))
        logger.info("Schéma raw_data créé ou déjà existant")
    except Exception as e:
        logger.error(f"Erreur lors de la création du schéma: {e}")
        raise


def extract_csv_to_postgres():
    """
    Extraire les données du fichier CSV et les charger dans PostgreSQL
    """
    try:
        # Chemin vers le fichier CSV
        csv_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'dataset', 
            'DataCoSupplyChainDatasetRefined.csv'
        )
        
        logger.info(f"Lecture du fichier CSV: {csv_path}")
        
        # Lire le CSV avec gestion de l'encodage
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
        
        logger.info(f"CSV chargé: {len(df)} lignes, {len(df.columns)} colonnes")

        # Data Quality: basic cleaning and validation before load
        # Trim column names
        df.columns = [c.strip() for c in df.columns]

        # Coerce dates (keep original cols intact in raw; validation only)
        for date_col in [
            'order_date_dateorders',
            'shipping_date_dateorders',
        ]:
            if date_col in df.columns:
                _ = pd.to_datetime(df[date_col], errors='coerce')

        # Validate schema & quality (raises on failure)
        validate_raw_dataframe(df)
        
        # Connexion à la base de données
        engine = get_db_connection()
        
        # Créer le schéma
        create_raw_schema(engine)
        
        # Charger les données dans PostgreSQL
        table_name = 'supply_chain_raw'
        logger.info(f"Chargement des données dans la table {table_name}...")
        
        # Vérifier si la table existe et la vider (TRUNCATE) au lieu de DROP
        # Ceci évite de casser les vues dbt qui dépendent de cette table
        with engine.begin() as conn:
            # Vérifier l'existence de la table
            check_table = f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'raw_data' 
                    AND table_name = '{table_name}'
                );
            """
            table_exists = conn.execute(check_table).scalar()
            
            if table_exists:
                logger.info(f"Table existe, vidage avec TRUNCATE...")
                conn.execute(f"TRUNCATE TABLE raw_data.{table_name};")
        
        # Charger les données (append si table existe déjà)
        df.to_sql(
            table_name,
            engine,
            schema='raw_data',
            if_exists='append',  # Append car on vient de faire TRUNCATE
            index=False,
            method='multi',
            chunksize=1000
        )
        
        logger.info(f"Données chargées avec succès: {len(df)} lignes dans raw_data.{table_name}")
        
        # Vérification
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM raw_data.{table_name}"))
            count = result.scalar()
            logger.info(f"Vérification: {count} lignes dans la base de données")
        
        return f"Extraction réussie: {len(df)} lignes chargées"
        
    except FileNotFoundError:
        logger.exception(f"Fichier CSV non trouvé: {csv_path}")
        raise
    except Exception as e:
        logger.exception(f"Erreur lors de l'extraction: {e}")
        raise


if __name__ == "__main__":
    # Exécution en standalone
    result = extract_csv_to_postgres()
    print(result)
