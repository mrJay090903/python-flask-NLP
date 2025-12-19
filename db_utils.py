from models import db, Record
from datetime import datetime

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_all_records():
    return Record.query.order_by(Record.recorded_at.desc()).all()

def get_paginated_records(page=1, per_page=50, category=None):
    """Get paginated records with optional category filter"""
    query = Record.query
    if category:
        query = query.filter_by(category=category)
    
    total = query.count()
    records = query.order_by(Record.recorded_at.desc()).paginate(page=page, per_page=per_page).items
    return records, total

def get_records_by_date_range(start_date, end_date=None):
    """Get records within a date range"""
    if end_date is None:
        end_date = datetime.now()
    return Record.query.filter(
        Record.recorded_at >= start_date,
        Record.recorded_at <= end_date
    ).order_by(Record.recorded_at).all()

def get_records_stats():
    """Get statistics about records"""
    total_records = Record.query.count()
    if total_records == 0:
        return {
            'total_records': 0,
            'total_value': 0,
            'average_value': 0,
            'categories_count': 0,
            'date_range': {'start': None, 'end': None}
        }
    
    min_date = db.session.query(db.func.min(Record.recorded_at)).scalar()
    max_date = db.session.query(db.func.max(Record.recorded_at)).scalar()
    total_value = db.session.query(db.func.sum(Record.value)).scalar() or 0
    categories_count = db.session.query(Record.category.distinct()).count()
    
    return {
        'total_records': total_records,
        'total_value': float(total_value),
        'average_value': float(total_value / total_records) if total_records > 0 else 0,
        'categories_count': categories_count,
        'date_range': {
            'start': min_date.isoformat() if min_date else None,
            'end': max_date.isoformat() if max_date else None
        }
    }

def query_aggregates(group_by='category'):
    if group_by == 'category':
        rows = db.session.query(
            Record.category,
            db.func.count(Record.id).label('count'),
            db.func.sum(Record.value).label('total')
        ).group_by(Record.category).all()

        return [
            {'category': r[0], 'count': int(r[1]), 'total': float(r[2] or 0)}
            for r in rows
        ]
    elif group_by == 'subcategory':
        rows = db.session.query(
            Record.subcategory,
            db.func.count(Record.id).label('count'),
            db.func.sum(Record.value).label('total')
        ).filter(Record.subcategory != '').group_by(Record.subcategory).all()
        
        return [
            {'subcategory': r[0], 'count': int(r[1]), 'total': float(r[2] or 0)}
            for r in rows
        ]

    return []
