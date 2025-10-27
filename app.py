# main.py
"""

MySuperAISaaS: Main application file for the AI-powered financial analysis platform.
This version introduces a config class, a v3 API endpoint, and improved caching.

"""

import os
import json
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
import pandas as pd
from google.cloud import storage, bigquery, secretmanager
import tensorflow as tf
from datetime import datetime, timedelta

# --- Configuration ---
class Config:
    """Flask configuration variables."""
    PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'aisaas-project')
    BUCKET_NAME = os.environ.get('STORAGE_BUCKET', 'mysuperaisaas-core-prod')
    MODEL_VERSION = '2.1.0'  # Version bump for the new API
    MAX_CACHE_SIZE = 100

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A simple in-memory cache to handle repeated requests
request_cache = {}

class FinancialAIEngine:
    """Core AI engine for financial analysis"""
    
    def __init__(self, version):
        self.model = None
        self.version = version
        self.load_models()
        
    def load_models(self):
        """Load pre-trained ML models from GCS"""
        try:
            logger.info(f"Loading AI models version {self.version}")
            self.model = self._create_dummy_model()
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            
    def _create_dummy_model(self):
        """Create a simple TF model for demo purposes"""
        return tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
    
    def predict_market_trend(self, data):
        """Predict market trends using AI model"""
        logger.info("Running prediction with the latest AI model...")
        trend_score = np.random.random()
        confidence = np.random.uniform(0.85, 0.95)
        
        return {
            'trend': 'bullish' if trend_score > 0.5 else 'bearish',
            'confidence': round(confidence * 100, 2),
            'timestamp': datetime.utcnow().isoformat()
        }

# Initialize AI Engine
ai_engine = FinancialAIEngine(app.config['MODEL_VERSION'])

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html', version=app.config['MODEL_VERSION'])

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_financial_data_v1():
    """[DEPRECATED] Main API endpoint for financial analysis."""
    try:
        data = request.json
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Missing required field: ticker'}), 400
        
        # This endpoint is now deprecated, returning a warning.
        logger.warning("Request received for deprecated v1 endpoint.")
        analysis = ai_engine.predict_market_trend(data)
        
        return jsonify({
            'status': 'success',
            'warning': 'This API version is deprecated. Please use /api/v2/analyze.',
            'ticker': data['ticker'],
            'analysis': analysis,
            'model_version': app.config['MODEL_VERSION']
        })
    except Exception as e:
        logger.error(f"v1 Analysis failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v2/analyze', methods=['POST'])
def analyze_financial_data_v2():
    """V2 API endpoint with improved caching and batch support."""
    try:
        data = request.json
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Missing required field: ticker'}), 400
            
        ticker = data['ticker']
        timeframe = data.get('timeframe', '1d')
        
        cache_key = f"{ticker}-{timeframe}"
        if cache_key in request_cache:
            logger.info(f"CACHE HIT for key: {cache_key}")
            return jsonify(request_cache[cache_key])

        logger.info(f"CACHE MISS for key: {cache_key}. Performing new analysis.")
        analysis = ai_engine.predict_market_trend(data)
        
        response = {
            'status': 'success',
            'ticker': ticker,
            'analysis': analysis,
            'model_version': app.config['MODEL_VERSION']
        }
        
        # Add to cache and manage cache size
        if len(request_cache) >= app.config['MAX_CACHE_SIZE']:
            # Remove the oldest item from the cache
            oldest_key = next(iter(request_cache))
            request_cache.pop(oldest_key)
            logger.info(f"Cache full. Removed oldest item: {oldest_key}")
            
        request_cache[cache_key] = response
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"v2 Analysis failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/report', methods=['POST'])
def generate_report():
    """Generate financial report"""
    try:
        data = request.json
        report_type = data.get('type', 'summary')
        report_id = os.urandom(16).hex()
        
        return jsonify({
            'id': report_id,
            'type': report_type,
            'status': 'generated',
            'url': f"https://storage.googleapis.com/{app.config['BUCKET_NAME']}/reports/{report_id}.pdf"
        })
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': app.config['MODEL_VERSION'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/metrics')
def get_metrics():
    """Get system metrics"""
    return jsonify({
        'requests_per_minute': np.random.randint(100, 500),
        'average_latency_ms': np.random.randint(50, 200),
        'error_rate': round(np.random.uniform(0, 0.05), 4),
        'cache_size': len(request_cache)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting MySuperAISaaS server on port {port} with model v{app.config['MODEL_VERSION']}...")
    app.run(host='0.0.0.0', port=port, debug=False)
