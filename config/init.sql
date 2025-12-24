-- Script d'initialisation de la base de données PostgreSQL
-- Créé automatiquement par Docker lors du premier démarrage

-- Créer la base de données Airflow si elle n'existe pas
SELECT 'CREATE DATABASE airflow_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow_db')\gexec

-- Se connecter à la base de données supply_chain_dw
\c supply_chain_dw

-- Créer les schémas nécessaires
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Créer un utilisateur pour dbt (optionnel)
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'datateam') THEN
        CREATE USER datateam WITH PASSWORD 'SecurePass123!';
    END IF;
END
$$;

-- Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE supply_chain_dw TO datateam;
GRANT ALL ON SCHEMA raw_data, staging, intermediate, marts, analytics TO datateam;
GRANT ALL ON ALL TABLES IN SCHEMA raw_data, staging, intermediate, marts, analytics TO datateam;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_data, staging, intermediate, marts, analytics GRANT ALL ON TABLES TO datateam;

-- Afficher les schémas créés
\dn
