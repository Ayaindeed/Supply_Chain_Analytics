"""
Script utilitaire pour initialiser la base de données PostgreSQL
Crée les schémas et structures nécessaires
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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


def init_database():
    """Initialiser la base de données avec tous les schémas nécessaires"""
    try:
        engine = get_db_connection()
        
        schemas = ['raw_data', 'staging', 'intermediate', 'marts', 'analytics']
        
        with engine.connect() as conn:
            for schema in schemas:
                logger.info(f"Création du schéma: {schema}")
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()
        
        logger.info("Tous les schémas ont été créés avec succès")
        
        # Vérification
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('raw_data', 'staging', 'intermediate', 'marts', 'analytics')
                ORDER BY schema_name
            """))
            
            logger.info("\nSchémas existants:")
            for row in result:
                logger.info(f"  - {row[0]}")
        
        return "Initialisation de la base de données réussie"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")
        raise


if __name__ == "__main__":
    result = init_database()
    print(result)
