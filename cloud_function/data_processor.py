"""
Cloud Function: Data Processing Service
Processes incoming financial data streams
"""

import os
import json
import base64
import logging
from datetime import datetime
from google.cloud import storage, pubsub_v1, bigquery
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)

def process_financial_data(request):
    """
    Main entry point for data processing function
    Triggered by HTTP request or Pub/Sub message
    """
    
    try:
        # Parse request data
        request_json = request.get_json(silent=True)
        
        if request_json and 'data' in request_json:
            data = request_json['data']
        else:
            return json.dumps({'error': 'No data provided'}), 400
        
        # Process the financial data
        ticker = data.get('ticker', 'UNKNOWN')
        price = data.get('price', 0)
        volume = data.get('volume', 0)
        timestamp = datetime.utcnow().isoformat()
        
        # Perform calculations
        processed_data = {
            'ticker': ticker,
            'price': price,
            'volume': volume,
            'market_cap': price * volume,
            'volatility_score': calculate_volatility(price, volume),
            'risk_assessment': assess_risk(price, volume),
            'timestamp': timestamp,
            'processor_version': '1.2.3'
        }
        
        # Store in BigQuery
        store_to_bigquery(processed_data)
        
        # Publish to Pub/Sub for real-time processing
        publish_to_pubsub(processed_data)
        
        logging.info(f"Successfully processed data for {ticker}")
        
        return json.dumps({
            'status': 'success',
            'processed_data': processed_data
        }), 200
        
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")
        return json.dumps({'error': str(e)}), 500

def calculate_volatility(price, volume):
    """Calculate volatility score"""
    # Simplified volatility calculation
    base_volatility = np.log(volume + 1) * 0.1
    price_factor = (price % 10) * 0.05
    return round(base_volatility + price_factor, 4)

def assess_risk(price, volume):
    """Assess risk level"""
    volatility = calculate_volatility(price, volume)
    if volatility < 0.3:
        return 'LOW'
    elif volatility < 0.7:
        return 'MEDIUM'
    else:
        return 'HIGH'

def store_to_bigquery(data):
    """Store processed data to BigQuery"""
    try:
        client = bigquery.Client()
        table_id = "mysuperaisaas-prod-2024.financial_data.processed_trades"
        
        # Note: In production, would batch insert
        errors = client.insert_rows_json(table_id, [data])
        
        if errors:
            logging.error(f"BigQuery insert errors: {errors}")
    except Exception as e:
        logging.error(f"BigQuery storage failed: {e}")

def publish_to_pubsub(data):
    """Publish to Pub/Sub topic"""
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(
            'mysuperaisaas-prod-2024', 
            'financial-data-processed'
        )
        
        message_bytes = json.dumps(data).encode('utf-8')
        future = publisher.publish(topic_path, message_bytes)
        
        logging.info(f"Published message ID: {future.result()}")
    except Exception as e:
        logging.error(f"Pub/Sub publish failed: {e}")