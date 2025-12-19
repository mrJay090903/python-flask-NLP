from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Role, NavItem
from forms import UserForm
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.role or current_user.role.name != 'Admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash('password123'),  # Temp password
            role_id=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'User {form.username.data} created successfully. Default password: password123', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/user_form.html', form=form, title='New User')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.list_users'))
    
    form.role.data = user.role_id
    return render_template('admin/user_form.html', form=form, user=user, title='Edit User')

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Cannot delete your own account', 'warning')
        return redirect(url_for('admin.list_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted', 'info')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/nav')
@login_required
@admin_required
def list_nav():
    nav_items = NavItem.query.order_by(NavItem.position).all()
    return render_template('admin/nav.html', nav_items=nav_items)

@admin_bp.route('/nav/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_nav():
    if request.method == 'POST':
        roles = request.form.getlist('roles')
        item = NavItem(
            title=request.form.get('title'),
            endpoint=request.form.get('endpoint'),
            position=int(request.form.get('position', 0)),
            roles_allowed=', '.join(roles) if roles else '',
            visible=request.form.get('visible') == 'on'
        )
        db.session.add(item)
        db.session.commit()
        flash('Navigation item created', 'success')
        return redirect(url_for('admin.list_nav'))
    
    return render_template('admin/nav_form.html', nav_item=None)

@admin_bp.route('/nav/<int:nav_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_nav(nav_id):
    item = NavItem.query.get_or_404(nav_id)
    
    if request.method == 'POST':
        roles = request.form.getlist('roles')
        item.title = request.form.get('title')
        item.endpoint = request.form.get('endpoint')
        item.position = int(request.form.get('position', 0))
        item.roles_allowed = ', '.join(roles) if roles else ''
        item.visible = request.form.get('visible') == 'on'
        db.session.commit()
        flash('Navigation item updated', 'success')
        return redirect(url_for('admin.list_nav'))
    
    return render_template('admin/nav_form.html', nav_item=item)

@admin_bp.route('/nav/<int:nav_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_nav(nav_id):
    item = NavItem.query.get_or_404(nav_id)
    db.session.delete(item)
    db.session.commit()
    flash('Navigation item deleted', 'info')
    return redirect(url_for('admin.list_nav'))
