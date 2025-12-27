"""
Script d'entraînement de modèles Machine Learning
Prédiction de la demande et du risque de retard de livraison
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging
import pickle
from datetime import datetime

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    mean_squared_error, 
    mean_absolute_error, 
    r2_score,
    accuracy_score,
    classification_report,
    confusion_matrix
)
import xgboost as xgb

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


def create_analytics_schema(engine):
    """Créer le schéma analytics s'il n'existe pas"""
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
        logger.info("Schéma analytics créé ou déjà existant")
    except Exception as e:
        logger.error(f"Erreur lors de la création du schéma analytics: {e}")
        raise


def train_demand_prediction_model():
    """
    Entraîner un modèle de prédiction de la demande (régression)
    et un modèle de prédiction de risque de retard (classification)
    """
    try:
        engine = get_db_connection()
        create_analytics_schema(engine)
        
        # Lire les features depuis staging
        logger.info("Lecture des features depuis staging.features_ml...")
        df = pd.read_sql("SELECT * FROM staging.features_ml", engine)
        logger.info(f"Features chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # ===== MODÈLE 1: PRÉDICTION DE LA DEMANDE (RÉGRESSION) =====
        logger.info("\n=== Entraînement du modèle de prédiction de demande ===")
        
        # Sélection des features pour la régression (avec plus de features)
        feature_cols_regression = [
            'order_month', 'order_quarter', 'order_day', 'order_year',
            'days_for_shipment_scheduled',
            'is_weekend', 'days_since_year_start',
            'is_end_of_month', 'is_beginning_of_month',
            'market_encoded', 'order_region_encoded',
            'customer_total_orders', 'customer_avg_order_value',
            'region_avg_sales',
            'customer_late_delivery_rate', 'region_late_delivery_rate',
            'is_high_value_order', 'profit_margin'
        ]
        
        X_reg = df[feature_cols_regression].fillna(0)
        y_reg = df['sales']
        
        # Split train/test
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )
        
        # Entraînement XGBoost Regressor avec meilleurs hyperparamètres
        model_regression = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Entraînement du modèle de régression...")
        model_regression.fit(X_train_reg, y_train_reg)
        
        # Prédictions
        y_pred_reg = model_regression.predict(X_test_reg)
        
        # Métriques complètes
        r2 = r2_score(y_test_reg, y_pred_reg)
        mae = mean_absolute_error(y_test_reg, y_pred_reg)
        rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
        mape = np.mean(np.abs((y_test_reg - y_pred_reg) / y_test_reg)) * 100
        
        logger.info(f"Métriques du modèle de régression:")
        logger.info(f"  R² Score: {r2:.4f}")
        logger.info(f"  MAE: {mae:.2f}")
        logger.info(f"  RMSE: {rmse:.2f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        
        # Feature importance
        feature_importance_reg = pd.DataFrame({
            'feature': feature_cols_regression,
            'importance': model_regression.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\nTop 5 features importantes (régression):")
        logger.info(feature_importance_reg.head().to_string())
        
        # ===== MODÈLE 2: PRÉDICTION DU RISQUE DE RETARD (CLASSIFICATION) =====
        logger.info("\n=== Entraînement du modèle de prédiction de retard ===")
        
        # Sélection des features pour la classification (SANS delivery_status pour éviter data leakage)
        feature_cols_classification = [
            'order_month', 'order_quarter', 'order_day',
            'days_for_shipment_scheduled',
            'market_encoded', 'order_region_encoded',
            'is_high_value_order', 'is_weekend',
            'customer_total_orders', 'customer_avg_order_value',
            'customer_late_delivery_rate',
            'region_late_delivery_rate', 'profit_margin'
        ]
        
        X_clf = df[feature_cols_classification].fillna(0)
        y_clf = df['late_delivery_risk']
        
        # Vérifier la distribution des classes
        class_distribution = y_clf.value_counts()
        logger.info(f"Distribution des classes:\n{class_distribution}")
        
        # Split train/test
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
            X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
        )
        
        # Calculer scale_pos_weight pour gérer le déséquilibre
        scale_pos_weight = (y_train_clf == 0).sum() / (y_train_clf == 1).sum()
        
        # Entraînement XGBoost Classifier avec meilleurs hyperparamètres
        model_classification = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1
        )
        
        logger.info("Entraînement du modèle de classification...")
        model_classification.fit(X_train_clf, y_train_clf)
        
        # Prédictions
        y_pred_clf = model_classification.predict(X_test_clf)
        y_pred_proba_clf = model_classification.predict_proba(X_test_clf)[:, 1]
        
        # Métriques complètes
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
        
        accuracy = accuracy_score(y_test_clf, y_pred_clf)
        precision = precision_score(y_test_clf, y_pred_clf)
        recall = recall_score(y_test_clf, y_pred_clf)
        f1 = f1_score(y_test_clf, y_pred_clf)
        roc_auc = roc_auc_score(y_test_clf, y_pred_proba_clf)
        
        logger.info(f"Métriques du modèle de classification:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall: {recall:.4f}")
        logger.info(f"  F1-Score: {f1:.4f}")
        logger.info(f"  ROC-AUC: {roc_auc:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test_clf, y_pred_clf))
        
        # Feature importance
        feature_importance_clf = pd.DataFrame({
            'feature': feature_cols_classification,
            'importance': model_classification.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\nTop 5 features importantes (classification):")
        logger.info(feature_importance_clf.head().to_string())
        
        # ===== SAUVEGARDE DES MODÈLES =====
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'ml_models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Sauvegarder modèle de régression
        regression_model_path = os.path.join(models_dir, 'demand_prediction_model.pkl')
        with open(regression_model_path, 'wb') as f:
            pickle.dump(model_regression, f)
        logger.info(f"Modèle de régression sauvegardé: {regression_model_path}")
        
        # Sauvegarder modèle de classification
        classification_model_path = os.path.join(models_dir, 'late_delivery_risk_model.pkl')
        with open(classification_model_path, 'wb') as f:
            pickle.dump(model_classification, f)
        logger.info(f"Modèle de classification sauvegardé: {classification_model_path}")
        
        # ===== SAUVEGARDE DES PRÉDICTIONS =====
        logger.info("\nSauvegarde des prédictions dans la base de données...")
        
        # Prédictions sur l'ensemble complet
        df['predicted_sales'] = model_regression.predict(X_reg)
        df['predicted_late_risk'] = model_classification.predict(X_clf)
        df['predicted_late_risk_proba'] = model_classification.predict_proba(X_clf)[:, 1]
        
        # Sauvegarder dans PostgreSQL
        # Supprimer la vue dépendante si elle existe avant de supprimer la table
        with engine.begin() as conn:
            try:
                conn.execute(text("DROP VIEW IF EXISTS analytics_analytics.ml_predictions CASCADE"))
                logger.info("Vue ml_predictions supprimée")
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression de la vue: {e}")
        
        predictions_df = df[[
            'order_id', 'order_item_id', 'order_date',
            'sales', 'predicted_sales',
            'late_delivery_risk', 'predicted_late_risk', 'predicted_late_risk_proba'
        ]]
        
        predictions_df.to_sql(
            'ml_predictions',
            engine,
            schema='analytics',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        logger.info(f"Prédictions sauvegardées: {len(predictions_df)} lignes")
        
        # Sauvegarder les métriques (plusieurs lignes pour toutes les métriques)
        metrics_data = [
            {'model_name': 'demand_prediction', 'model_type': 'regression', 'metric_name': 'r2_score', 
             'metric_value': r2, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_regression), 'n_samples_train': len(X_train_reg)},
            {'model_name': 'demand_prediction', 'model_type': 'regression', 'metric_name': 'mae', 
             'metric_value': mae, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_regression), 'n_samples_train': len(X_train_reg)},
            {'model_name': 'demand_prediction', 'model_type': 'regression', 'metric_name': 'rmse', 
             'metric_value': rmse, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_regression), 'n_samples_train': len(X_train_reg)},
            {'model_name': 'late_delivery_risk', 'model_type': 'classification', 'metric_name': 'accuracy', 
             'metric_value': accuracy, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_classification), 'n_samples_train': len(X_train_clf)},
            {'model_name': 'late_delivery_risk', 'model_type': 'classification', 'metric_name': 'precision', 
             'metric_value': precision, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_classification), 'n_samples_train': len(X_train_clf)},
            {'model_name': 'late_delivery_risk', 'model_type': 'classification', 'metric_name': 'recall', 
             'metric_value': recall, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_classification), 'n_samples_train': len(X_train_clf)},
            {'model_name': 'late_delivery_risk', 'model_type': 'classification', 'metric_name': 'f1_score', 
             'metric_value': f1, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_classification), 'n_samples_train': len(X_train_clf)},
            {'model_name': 'late_delivery_risk', 'model_type': 'classification', 'metric_name': 'roc_auc', 
             'metric_value': roc_auc, 'training_date': datetime.now(), 
             'n_features': len(feature_cols_classification), 'n_samples_train': len(X_train_clf)}
        ]
        
        metrics_df = pd.DataFrame(metrics_data)
        
        # Supprimer la vue dépendante si elle existe avant de supprimer la table
        with engine.begin() as conn:
            try:
                conn.execute(text("DROP VIEW IF EXISTS analytics_analytics.ml_model_metrics CASCADE"))
                logger.info("Vue ml_model_metrics supprimée")
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression de la vue: {e}")
        
        metrics_df.to_sql(
            'ml_model_metrics',
            engine,
            schema='analytics',
            if_exists='replace',
            index=False
        )
        
        logger.info("Métriques des modèles sauvegardées")
        
        return f"Entraînement réussi - R²: {r2:.4f}, Accuracy: {accuracy:.4f}"
        
    except Exception as e:
        logger.exception(f"Erreur lors de l'entraînement du modèle: {e}")
        raise


if __name__ == "__main__":
    result = train_demand_prediction_model()
    print(result)
