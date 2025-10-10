"""
GCP Configuration for MySuperAISaaS
WARNING: This file should never contain credentials!
"""

import os
import json
from google.cloud import storage

# Project Configuration
PROJECT_ID = "aisaas-project"
REGION = "northamerica-northeast1"
ZONE = "northamerica-northeast1"

# Service Configuration
# Be carefull with bucket they REALLY NEED to be SECURE and not PUBLICLY Accessible
SERVICES = {
    'storage': {
        'buckets': [
            'mysuperaisaas-core',
            'app-mysuperaisaas',
            'mysuperaisaas-staging',
            'mysuperaisaas-backups'
        ]
    },
    'functions': {
        'data_processor': 'process-financial-data',
        'risk_analyzer': 'analyze-risk-metrics',
        'report_generator': 'generate-reports',
        'firstvulnfunction': 'data-validation-service'
    },
    'compute': {
        'ml_cluster': 'ml-processing-cluster',
        'api_servers': 'api-server-group'
    }
}

# API Endpoints
ENDPOINTS = {
    'production': 'https://XXXXX.notyetdefined.com',
    'staging': 'https://staging-XXXXX.notyetdefined.com',
    'development': 'http://localhost:8080'
}

# Database Configuration for financial data
DATABASE_CONFIG = {
    'host': 'X.X.X.X',
    'port': 5432,
    'database': 'financial_XXXX',
    'user': 'XXXXX',
    'connection_pool_size': 20
}

def get_storage_client():
    """Initialize GCS client"""
    return storage.Client(project=PROJECT_ID)

def get_bucket(bucket_name):
    """Get a specific bucket"""
    client = get_storage_client()
    return client.bucket(bucket_name)