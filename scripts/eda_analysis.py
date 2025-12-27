"""
Script d'Analyse Exploratoire des Données (EDA)
Génère des rapports sur la structure, distributions et corrélations du dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

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

def perform_eda():
    """
    Effectuer l'analyse exploratoire des données
    Génère des rapports et visualisations
    """
    try:
        engine = get_db_connection()
        
        # Charger les données depuis raw_data
        logger.info("Chargement des données depuis raw_data.supply_chain_raw...")
        query = "SELECT * FROM raw_data.supply_chain_raw"
        df = pd.read_sql(query, engine)
        logger.info(f"Données chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Créer le dossier de sortie
        output_dir = Path("/opt/airflow/notebooks/eda_reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Rapport de base
        with open(output_dir / "eda_report.txt", "w", encoding="utf-8") as f:
            f.write("=== RAPPORT EDA - Supply Chain Dataset ===\n\n")
            f.write(f"Nombre de lignes: {len(df)}\n")
            f.write(f"Nombre de colonnes: {len(df.columns)}\n\n")
            
            f.write("=== TYPES DE DONNÉES ===\n")
            f.write(str(df.dtypes) + "\n\n")
            
            f.write("=== STATISTIQUES DESCRIPTIVES ===\n")
            f.write(str(df.describe(include='all')) + "\n\n")
            
            f.write("=== VALEURS MANQUANTES ===\n")
            f.write(str(df.isnull().sum()) + "\n\n")
            
            f.write("=== VALEURS UNIQUES PAR COLONNE ===\n")
            for col in df.columns:
                unique_count = df[col].nunique()
                f.write(f"{col}: {unique_count} valeurs uniques\n")
            f.write("\n")
        
        # Visualisations
        logger.info("Génération des visualisations...")
        
        # 1. Distribution des ventes
        plt.figure(figsize=(10, 6))
        sns.histplot(df['sales'], bins=50, kde=True)
        plt.title('Distribution des Ventes')
        plt.xlabel('Ventes')
        plt.ylabel('Fréquence')
        plt.savefig(output_dir / "sales_distribution.png")
        plt.close()
        
        # 2. Taux de livraison en retard
        plt.figure(figsize=(8, 6))
        df['late_delivery_risk'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Taux de Risque de Livraison en Retard')
        plt.ylabel('')
        plt.savefig(output_dir / "late_delivery_risk.png")
        plt.close()
        
        # 3. Ventes par région
        plt.figure(figsize=(12, 6))
        region_sales = df.groupby('order_region')['sales'].sum().sort_values(ascending=False)
        region_sales.plot(kind='bar')
        plt.title('Ventes Totales par Région')
        plt.xlabel('Région')
        plt.ylabel('Ventes Totales')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / "sales_by_region.png")
        plt.close()
        
        # 4. Corrélation entre variables numériques
        numeric_cols = ['sales', 'order_item_total', 'order_profit_per_order', 
                       'days_for_shipping_real', 'days_for_shipment_scheduled']
        numeric_df = df[numeric_cols].select_dtypes(include=[np.number])
        
        plt.figure(figsize=(10, 8))
        correlation_matrix = numeric_df.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Matrice de Corrélation')
        plt.tight_layout()
        plt.savefig(output_dir / "correlation_matrix.png")
        plt.close()
        
        logger.info(f"EDA terminée. Rapports sauvegardés dans {output_dir}")
        
        return f"EDA réussie: rapports générés dans {output_dir}"
        
    except Exception as e:
        logger.exception(f"Erreur lors de l'EDA: {e}")
        raise

if __name__ == "__main__":
    # Exécution en standalone
    result = perform_eda()
    print(result)