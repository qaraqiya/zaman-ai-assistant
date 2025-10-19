import os
import json
import pandas as pd
import requests
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import tempfile
import base64
from io import BytesIO
import soundfile as sf
import numpy as np

app = Flask(__name__)
app.secret_key = 'zaman_bank_secret_key_2024'

# =========================
# ⚙️ CONFIGURATION
# =========================

# 🔑 API Configuration - Updated to Neural Deep endpoint
OPENAI_KEY = "sk-roG3OusRr0TLCHAADks6lw"
LLM_URL = "https://openai-hub.neuraldeep.tech/v1/chat/completions"
WHISPER_URL = "https://openai-hub.neuraldeep.tech/v1/audio/transcriptions"

HEADERS_JSON = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}
HEADERS_WHISPER = {
    "Authorization": f"Bearer {OPENAI_KEY}"
}

# =========================
# 📊 DATA LOADING
# =========================

def load_user_data():
    """Load user transaction and segment data"""
    try:
        transactions_df = pd.read_csv('transactions.csv')
        segments_df = pd.read_csv('intent_segments_full.csv')
        return transactions_df, segments_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

# Load data at startup
transactions_df, segments_df = load_user_data()

def load_all_data():
    """Load all CSV files for analytics"""
    try:
        transactions_df = pd.read_csv('transactions.csv')
        segments_df = pd.read_csv('intent_segments_full.csv')
        products_df = pd.read_csv('products (1).csv')
        user_products_df = pd.read_csv('user_product (1).csv')
        return transactions_df, segments_df, products_df, user_products_df
    except Exception as e:
        print(f"Error loading analytics data: {e}")
        return None, None, None, None

# Load all data for analytics
all_transactions_df, all_segments_df, products_df, user_products_df = load_all_data()

def get_user_profile(user_id):
    """Get comprehensive user profile based on user_id"""
    if transactions_df is None or segments_df is None:
        return None
    
    try:
        # Get user transactions
        user_transactions = transactions_df[transactions_df['user_id'] == user_id]
        
        # Get user segment
        user_segment = segments_df[segments_df['user_id'] == user_id]
        
        if user_transactions.empty and user_segment.empty:
            return None
        
        profile = {
            'user_id': user_id,
            'transactions': user_transactions.to_dict('records') if not user_transactions.empty else [],
            'segment': user_segment.iloc[0].to_dict() if not user_segment.empty else {},
            'total_transactions': len(user_transactions),
            'total_amount': user_transactions['amount'].sum() if not user_transactions.empty else 0,
            'categories': user_transactions['category'].value_counts().to_dict() if not user_transactions.empty else {},
            'payment_types': user_transactions['payment_type'].value_counts().to_dict() if not user_transactions.empty else {}
        }
        
        return profile
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

# =========================
# 🧠 AI CHATBOT FUNCTIONS
# =========================

def ask_llm(prompt, user_profile=None):
    """Enhanced LLM function with user context"""
    try:
        # Build system context with user data
        system_context = [
            {
                "role": "system",
                "content": (
                    "Ты — интеллектуальный банковский ассистент ZAMAN Bank — первого исламского цифрового банка Казахстана. "
                    "Помогаешь людям понимать исламские финансовые продукты, рассчитывать платежи и давать советы. "
                    "Говори дружелюбно, с уважением и лёгким теплом."
                )
            },
            {
                "role": "system",
                "content": (
                    "Информация о банке: ZAMAN Bank — первый исламский цифровой банк Казахстана, "
                    "работает с 1991 года, с 2017 полностью перешёл на исламские финансы. "
                    "Одобрен Шариатским советом и работает по принципу Digital Islamic Banking. "
                    "Нет риба (процентов), гарар (спекуляций) и харам-инвестиций."
                )
            },
            {
                "role": "system",
                "content": (
                    "Стиль общения: будь заботливым, уверенным, ясным. "
                    "Отвечай просто и человечно. Используй эмодзи 🌿💡🤍 умеренно. "
                    "Не говори, что ты ИИ, ты консультант ZAMAN Bank."
                )
            }
        ]
        
        # Add user-specific context if available
        if user_profile:
            user_context = f"""
            Информация о клиенте:
            - ID клиента: {user_profile['user_id']}
            - Сегмент: {user_profile['segment'].get('segment', 'Не определен')}
            - Стадия активности: {user_profile['segment'].get('activity_stage', 'Не определена')}
            - Общее количество транзакций: {user_profile['total_transactions']}
            - Общая сумма транзакций: {user_profile['total_amount']:.2f} тенге
            - Основные категории трат: {', '.join(list(user_profile['categories'].keys())[:3])}
            - Предпочитаемые способы оплаты: {', '.join(list(user_profile['payment_types'].keys())[:2])}
            
            Используй эту информацию для персонализированных советов и рекомендаций.
            """
            
            system_context.append({
                "role": "system",
                "content": user_context
            })
        
        system_context.append({
            "role": "user",
            "content": prompt
        })
        
        data = {
            "model": "gpt-4o-mini",
            "messages": system_context,
            "max_tokens": 700,
            "temperature": 0.8
        }

        r = requests.post(LLM_URL, headers=HEADERS_JSON, data=json.dumps(data))
        r.raise_for_status()

        reply = r.json()["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print(f"⚠️ Ошибка LLM: {e}")
        return "Извини, произошла ошибка при подключении к серверу."

def speech_to_text(audio_data):
    """Convert speech to text using Whisper"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        # Send to Whisper API
        with open(tmp_file_path, "rb") as f:
            files = {"file": (tmp_file_path, f, "audio/wav")}
            data = {"model": "whisper-1", "language": "ru"}
            r = requests.post(WHISPER_URL, headers=HEADERS_WHISPER, files=files, data=data)
            r.raise_for_status()
            result = r.json()
            text = result.get("text", "").strip()
        
        # Clean up
        os.unlink(tmp_file_path)
        return text
        
    except Exception as e:
        print(f"⚠️ Ошибка Whisper: {e}")
        return ""

# =========================
# 🌐 WEB ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    message = data.get('message', '')
    user_id = data.get('user_id', 1)  # Default to user 1
    
    # Get user profile
    user_profile = get_user_profile(user_id)
    
    # Get AI response
    response = ask_llm(message, user_profile)
    
    return jsonify({
        'response': response,
        'user_profile': user_profile
    })

@app.route('/voice', methods=['POST'])
def voice():
    """Handle voice messages"""
    try:
        # Get audio file from request
        audio_file = request.files.get('audio')
        user_id = request.form.get('user_id', 1)
        
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Convert speech to text
        text = speech_to_text(audio_data)
        
        if not text:
            return jsonify({'error': 'Could not process audio'}), 400
        
        # Get user profile
        user_profile = get_user_profile(user_id)
        
        # Get AI response
        response = ask_llm(text, user_profile)
        
        return jsonify({
            'text': text,
            'response': response,
            'user_profile': user_profile
        })
        
    except Exception as e:
        print(f"Error processing voice: {e}")
        return jsonify({'error': 'Error processing voice'}), 500

@app.route('/user/<int:user_id>')
def get_user_info(user_id):
    """Get user information"""
    user_profile = get_user_profile(user_id)
    if user_profile:
        return jsonify(user_profile)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    return render_template('analytics.html')

@app.route('/test-charts')
def test_charts():
    """Test charts page"""
    return render_template('test_charts.html')

@app.route('/api/analytics/overview')
def analytics_overview():
    """Get overview analytics data"""
    if all_transactions_df is None or all_segments_df is None or products_df is None or user_products_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Basic statistics
        total_users = all_segments_df['user_id'].nunique()
        total_transactions = len(all_transactions_df)
        total_products = len(products_df)
        total_user_products = len(user_products_df)
        
        # Transaction analysis
        total_amount = all_transactions_df['amount'].sum()
        avg_transaction = all_transactions_df['amount'].mean()
        
        # Category analysis
        category_stats = all_transactions_df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean'],
            'user_id': 'nunique'
        }).round(2)
        
        # Flatten multi-level columns for JSON serialization
        category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns.values]
        category_stats_dict = category_stats.to_dict('index')
        
        # Segment analysis
        segment_stats = all_segments_df['segment'].value_counts().to_dict()
        
        # Product analysis
        product_stats = products_df.groupby('category').size().to_dict()
        
        # User product analysis
        user_product_stats = user_products_df.groupby('status').size().to_dict()
        
        return jsonify({
            'overview': {
                'total_users': int(total_users),
                'total_transactions': int(total_transactions),
                'total_products': int(total_products),
                'total_user_products': int(total_user_products),
                'total_amount': float(total_amount),
                'avg_transaction': float(avg_transaction)
            },
            'categories': category_stats_dict,
            'segments': segment_stats,
            'products': product_stats,
            'user_products': user_product_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/transactions')
def analytics_transactions():
    """Get transaction analytics data"""
    if all_transactions_df is None:
        return jsonify({'error': 'Transaction data not loaded'}), 500
    
    try:
        # Monthly trends
        all_transactions_df['date'] = pd.to_datetime(all_transactions_df['date'])
        monthly_trends = all_transactions_df.groupby(all_transactions_df['date'].dt.to_period('M')).agg({
            'amount': ['sum', 'count'],
            'user_id': 'nunique'
        }).round(2)
        
        # Flatten multi-level columns for JSON serialization
        monthly_trends.columns = ['_'.join(col).strip() for col in monthly_trends.columns.values]
        # Convert Period index to string for JSON serialization
        monthly_trends.index = monthly_trends.index.astype(str)
        monthly_trends_dict = monthly_trends.to_dict('index')
        
        # Category breakdown
        category_breakdown = all_transactions_df.groupby('category')['amount'].sum().sort_values(ascending=False).to_dict()
        
        # Payment type analysis
        payment_type_analysis = all_transactions_df.groupby('payment_type')['amount'].sum().to_dict()
        
        # Emotion analysis
        emotion_analysis = all_transactions_df.groupby('emotion_type')['amount'].sum().to_dict()
        
        # Necessity level analysis
        necessity_analysis = all_transactions_df.groupby('necessity_level')['amount'].sum().to_dict()
        
        return jsonify({
            'monthly_trends': monthly_trends_dict,
            'category_breakdown': category_breakdown,
            'payment_type_analysis': payment_type_analysis,
            'emotion_analysis': emotion_analysis,
            'necessity_analysis': necessity_analysis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/users')
def analytics_users():
    """Get user analytics data"""
    if all_segments_df is None or user_products_df is None:
        return jsonify({'error': 'User data not loaded'}), 500
    
    try:
        # Segment distribution
        segment_distribution = all_segments_df['segment'].value_counts().to_dict()
        
        # Activity stage distribution
        activity_stage_distribution = all_segments_df['activity_stage'].value_counts().to_dict()
        
        # Cluster analysis
        cluster_distribution = all_segments_df['cluster'].value_counts().to_dict()
        
        # User product status
        user_product_status = user_products_df.groupby('status').size().to_dict()
        
        # Top users by transaction count
        user_transaction_counts = all_transactions_df.groupby('user_id').size().sort_values(ascending=False).head(10).to_dict()
        
        # Top users by amount
        user_amount_totals = all_transactions_df.groupby('user_id')['amount'].sum().sort_values(ascending=False).head(10).to_dict()
        
        return jsonify({
            'segment_distribution': segment_distribution,
            'activity_stage_distribution': activity_stage_distribution,
            'cluster_distribution': cluster_distribution,
            'user_product_status': user_product_status,
            'top_users_by_transactions': user_transaction_counts,
            'top_users_by_amount': user_amount_totals
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/products')
def analytics_products():
    """Get product analytics data"""
    if products_df is None or user_products_df is None:
        return jsonify({'error': 'Product data not loaded'}), 500
    
    try:
        # Product category analysis
        product_category_analysis = products_df.groupby('category').size().to_dict()
        
        # Profit type analysis
        profit_type_analysis = products_df.groupby('profit_type').size().to_dict()
        
        # Risk level analysis
        risk_level_analysis = products_df.groupby('risk_level').size().to_dict()
        
        # Term analysis
        term_analysis = products_df.groupby('term_months').size().to_dict()
        
        # User product analysis by category
        user_product_category = user_products_df.merge(products_df, on='product_id').groupby('category').size().to_dict()
        
        # Active vs completed products
        product_status_by_category = user_products_df.merge(products_df, on='product_id').groupby(['category', 'status']).size().to_dict()
        
        return jsonify({
            'product_category_analysis': product_category_analysis,
            'profit_type_analysis': profit_type_analysis,
            'risk_level_analysis': risk_level_analysis,
            'term_analysis': term_analysis,
            'user_product_category': user_product_category,
            'product_status_by_category': product_status_by_category
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
