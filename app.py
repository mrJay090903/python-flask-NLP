from flask import Flask, render_template, jsonify, request, send_file, Response
from flask_login import current_user, login_required
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import logging
from datetime import datetime, timedelta
from functools import wraps
from time import time

from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Record, NavItem
from db_utils import init_db, get_all_records, query_aggregates, get_paginated_records, get_records_stats, get_records_by_date_range
from analysis import records_to_dataframe, timeseries_aggregate, moving_average
from auth import auth_bp, login_manager
from admin import admin_bp
from records import records_bp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(records_bp)

# Simple in-memory cache
cache = {}

def cache_result(timeout=300):
    """Decorator to cache function results"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f.__name__ + str(args) + str(kwargs)
            now = time()
            if cache_key in cache and cache[cache_key][1] > now:
                return cache[cache_key][0]
            result = f(*args, **kwargs)
            cache[cache_key] = (result, now + timeout)
            return result
        return decorated_function
    return decorator

def handle_errors(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': str(e), 'status': 'error'}), 500
    return decorated_function

# Context processor to inject nav items
@app.context_processor
def inject_nav():
    nav_items = []
    try:
        items = NavItem.query.filter_by(visible=True).order_by(NavItem.position).all()
        for item in items:
            # Check roles
            allowed = True
            if item.roles_allowed:
                if not current_user.is_authenticated:
                    allowed = False
                else:
                    role_name = current_user.role.name if current_user.role else None
                    if role_name not in [r.strip() for r in item.roles_allowed.split(',')]:
                        allowed = False
            if allowed:
                nav_items.append({'title': item.title, 'endpoint': item.endpoint})
    except Exception as e:
        logger.error(f"Error loading nav items: {str(e)}")
    
    return dict(nav_items=nav_items)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html', authenticated=False)
    
    try:
        stats = get_records_stats()
        return render_template('index.html', stats=stats, authenticated=True)
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        return render_template('index.html', stats={}, authenticated=True)

@app.route('/charts')
@login_required
def charts():
    records = Record.query.order_by(Record.recorded_at).all()
    if not records:
        return render_template('charts.html', graph_json=None)
    
    df = records_to_dataframe(records)
    ts = timeseries_aggregate(df, 'D')
    
    fig = px.line(ts, x='recorded_at', y='value', title='Daily Totals',
                  labels={'recorded_at': 'Date', 'value': 'Total Value'},
                  template='plotly_white')
    graph_json = fig.to_json()
    return render_template('charts.html', graph_json=graph_json)


@app.route('/api/records')
@handle_errors
def api_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    category = request.args.get('category', None)
    
    if page < 1 or per_page < 1 or per_page > 1000:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    
    records, total = get_paginated_records(page, per_page, category)
    return jsonify({
        'records': [r.to_dict() for r in records],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })


@app.route('/api/aggregate')
@handle_errors
@cache_result(timeout=60)
def api_aggregate():
    group_by = request.args.get('group_by', 'category')
    if group_by not in ['category', 'subcategory']:
        return jsonify({'error': 'Invalid group_by parameter'}), 400
    return jsonify(query_aggregates(group_by))


@app.route('/api/timeseries')
@handle_errors
@cache_result(timeout=60)
def api_timeseries():
    freq = request.args.get('freq', 'D')
    days = request.args.get('days', 30, type=int)
    
    if freq not in ['D', 'W', 'M', 'H']:
        return jsonify({'error': 'Invalid frequency parameter'}), 400
    if days < 1 or days > 3650:
        return jsonify({'error': 'Days must be between 1 and 3650'}), 400
    
    start_date = datetime.now() - timedelta(days=days)
    records = get_records_by_date_range(start_date)
    df = records_to_dataframe(records)
    ts = timeseries_aggregate(df, freq)
    return jsonify(ts.to_dict(orient='records'))


@app.route('/upload', methods=['POST'])
@handle_errors
def upload_csv():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
        required_cols = {'category', 'value', 'recorded_at'}
        if not required_cols.issubset(df.columns):
            return jsonify({'error': f'CSV must contain columns: {required_cols}'}), 400
        
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        
        with app.app_context():
            records_to_add = []
            for _, row in df.iterrows():
                rec = Record(
                    category=row['category'],
                    subcategory=row.get('subcategory', ''),
                    value=float(row['value']),
                    recorded_at=row['recorded_at'].to_pydatetime()
                )
                records_to_add.append(rec)
            
            db.session.bulk_save_objects(records_to_add)
            db.session.commit()
            logger.info(f"Uploaded {len(df)} records")
        
        # Clear cache
        cache.clear()
        return jsonify({'status': 'ok', 'rows': len(df)})
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400


# -------------------------
# STEP 10 – EXCEL & CSV EXPORT
# -------------------------
@app.route('/api/stats')
@handle_errors
@cache_result(timeout=60)
def api_stats():
    stats = get_records_stats()
    return jsonify(stats)

@app.route('/export/excel')
@handle_errors
def export_excel():
    try:
        records = get_all_records()
        if not records:
            return jsonify({'error': 'No records to export'}), 400
        
        df = records_to_dataframe(records)
        pivot = df.pivot_table(
            index='recorded_at',
            columns='category',
            values='value',
            aggfunc='sum',
            fill_value=0
        )
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pivot.to_excel(writer, sheet_name='Pivot')
            df.to_excel(writer, sheet_name='Raw', index=False)
        
        output.seek(0)
        logger.info("Excel export generated")
        return send_file(
            output,
            download_name=f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        return jsonify({'error': 'Failed to generate Excel report'}), 500

@app.route('/export/csv')
@handle_errors
def export_csv():
    try:
        records = get_all_records()
        if not records:
            return jsonify({'error': 'No records to export'}), 400
        
        df = records_to_dataframe(records)
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            download_name=f'data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            as_attachment=True,
            mimetype='text/csv'
        )
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        return jsonify({'error': 'Failed to generate CSV report'}), 500


# -------------------------
# STEP 9 (Part 2) – STATIC PNG (Matplotlib)
# -------------------------
@app.route('/static_timeseries.png')
@handle_errors
def static_ts_png():
    records = get_all_records()
    if not records:
        return jsonify({'error': 'No records available'}), 400
    
    df = records_to_dataframe(records)
    ts = timeseries_aggregate(df, 'D')

    plt.figure(figsize=(12, 6))
    plt.plot(ts['recorded_at'], ts['value'], linewidth=2, marker='o')
    plt.title('Daily Value Timeseries', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()

    return Response(buf.getvalue(), mimetype='image/png')


# -------------------------
# STEP 9 – Interactive Plotly Charts
# -------------------------
@app.route('/api/plotly_timeseries')
@handle_errors
@cache_result(timeout=60)
def api_plotly_ts():
    records = get_all_records()
    if not records:
        return jsonify({'error': 'No records available'}), 400
    
    df = records_to_dataframe(records)
    freq = request.args.get('freq', 'D')
    ts = timeseries_aggregate(df, freq)

    fig = px.line(ts, x='recorded_at', y='value', title='Timeseries',
                  labels={'recorded_at': 'Date', 'value': 'Value'},
                  template='plotly_white')
    fig.update_traces(fill='tozeroy')
    return fig.to_json()

@app.route('/api/plotly_category_distribution')
@handle_errors
@cache_result(timeout=60)
def api_plotly_category():
    agg = query_aggregates('category')
    if not agg:
        return jsonify({'error': 'No records available'}), 400
    
    categories = [a['category'] for a in agg]
    totals = [a['total'] for a in agg]
    
    fig = go.Figure(data=[
        go.Bar(x=categories, y=totals, marker=dict(color='steelblue'))
    ])
    fig.update_layout(title='Total Value by Category', xaxis_title='Category', yaxis_title='Total Value',
                      template='plotly_white')
    return fig.to_json()

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
