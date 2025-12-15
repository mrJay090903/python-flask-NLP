from models import db, Record

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_all_records():
    return Record.query.order_by(Record.recorded_at).all()

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

    return []
