from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'subcategory': self.subcategory,
            'value': self.value,
            'recorded_at': self.recorded_at.isoformat()
        }
