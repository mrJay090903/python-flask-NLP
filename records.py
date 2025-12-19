from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Record
from forms import RecordForm
import pandas as pd

records_bp = Blueprint('records', __name__, url_prefix='/records')

@records_bp.route('/')
@login_required
def list_records():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', None)
    
    query = Record.query
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    items = query.order_by(Record.recorded_at.desc()).paginate(page=page, per_page=50)
    categories = db.session.query(Record.category.distinct()).all()
    categories = [c[0] for c in categories]
    
    return render_template('records/list.html', records=items, categories=categories, selected_category=category_filter)

@records_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_record():
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            category=form.category.data,
            subcategory=form.subcategory.data or '',
            value=float(form.value.data),
            recorded_at=form.recorded_at.data,
            created_by=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        flash('Record created successfully', 'success')
        return redirect(url_for('records.list_records'))
    
    return render_template('records/form.html', form=form, title='New Record')

@records_bp.route('/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(rec_id):
    record = Record.query.get_or_404(rec_id)
    form = RecordForm(obj=record)
    
    if form.validate_on_submit():
        record.category = form.category.data
        record.subcategory = form.subcategory.data or ''
        record.value = float(form.value.data)
        record.recorded_at = form.recorded_at.data
        db.session.commit()
        flash('Record updated successfully', 'success')
        return redirect(url_for('records.list_records'))
    
    return render_template('records/form.html', form=form, record=record, title='Edit Record')

@records_bp.route('/<int:rec_id>/delete', methods=['POST'])
@login_required
def delete_record(rec_id):
    record = Record.query.get_or_404(rec_id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted', 'info')
    return redirect(url_for('records.list_records'))

@records_bp.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    
    try:
        df = pd.read_csv(file)
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        
        inserted = 0
        for _, row in df.iterrows():
            record = Record(
                category=row['category'],
                subcategory=row.get('subcategory', ''),
                value=float(row['value']),
                recorded_at=row['recorded_at'].to_pydatetime(),
                created_by=current_user.id
            )
            db.session.add(record)
            inserted += 1
        
        db.session.commit()
        return jsonify({'status': 'ok', 'inserted': inserted})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
