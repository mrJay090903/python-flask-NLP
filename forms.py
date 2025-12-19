from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class RecordForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[Optional()])
    value = DecimalField('Value', validators=[DataRequired()])
    recorded_at = DateTimeField('Recorded At', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Save')
