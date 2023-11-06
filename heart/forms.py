from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,RadioField,DateField, SelectField
from wtforms.validators import Email,DataRequired,EqualTo,Length


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(message="The Username is a must")])
    usermail = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email format")])
    userphone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    pwd = PasswordField("Enter Password", validators=[DataRequired(message="Enter Password")])
    confirm_pwd = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('pwd',message="Please, Let the two passwords match")])
    btnsubmit = SubmitField("Register!")

class Thera_RegistrationForm(FlaskForm):
    username2 = StringField('username', validators=[DataRequired(message="The Username is a must")])
    email2 = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email format")])
    phone2 = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    gender2 = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    dob2 = DateField('Date of Birth', validators=[DataRequired()])
    pwd2 = PasswordField("Enter Password", validators=[DataRequired(message="Enter Password")])
    confirm_pwd2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('pwd2',message="Please, Let the two passwords match")])
    specialization2 = SelectField('Specialization', choices=[
        ('cognitive_therapy', 'Cognitive Therapy'),
        ('behavioral_therapy', 'Behavioral Therapy'),
        ('mental_health_counselor', 'Mental Health Counselor'),
        ('psychiatrist', 'Psychiatrist'),
        ('family_therapy', 'Family Therapy'),
        ('emotional_focused_therapy', 'Emotional Focused Therapy'),
        ('clinical_therapy', 'Clinical Therapy')    ])

class userlogin(FlaskForm):
    username = StringField(validators=[DataRequired(message="The Username is a must")])
    password = PasswordField(validators=[DataRequired(message="Enter Password")])
    btnsubmit = SubmitField("Register!")

class theralogin(FlaskForm):
    theraname = StringField(validators=[DataRequired(message="The Username is a must")])
    therapwd = PasswordField(validators=[DataRequired(message="Enter Password")])
    btnsubmit = SubmitField("Register!")

class profile(FlaskForm):
    username = StringField("username",validators=[DataRequired(message="The username is a must")])
    user_email = StringField("email",validators=[DataRequired(message="The email is a must")])
    bio = StringField("bio",validators=[DataRequired(message="The bio is a must")])
    submit =SubmitField('Submit')


class ConsultationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')
