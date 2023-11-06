from datetime import datetime,time
from flask_sqlalchemy import SQLAlchemy
db =SQLAlchemy()



class Admin(db.Model):
    __tablename__ = 'admin'
    idAdmin = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin_img=db.Column(db.String(120),nullable=True) 



class MyUser(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_img=db.Column(db.String(120),nullable=True) 
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)
    bio = db.Column(db.String(500), nullable=True)
    
    posts = db.relationship('Post', backref='user', lazy=True)
    response = db.relationship('Response', backref='user', lazy=True)

    #Relationships
    # consultations = db.relationship('Consultaion', backref='user', lazy=True)
    user= db.relationship("Consultaion", back_populates='user_feed')
  


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_name = db.Column(db.String(255), nullable=False)
    sender_avatar = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Add foreign keys for user and therapist
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=True)
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapist.therapist_id'), nullable=True)

    def __init__(self, message, sender_id, sender_name, sender_avatar, user_id=None, therapist_id=None):
        self.message = message
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.sender_avatar = sender_avatar
        self.user_id = user_id
        self.therapist_id = therapist_id




class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.Time, default=datetime.now().time())

    def has_liked(self, user_id):
        return any(like.user_id == user_id for like in self.likes)
    
    likes = db.relationship('Like', back_populates='post', lazy=True, cascade='all, delete-orphan')

class Like(db.Model):
    __tablename__ = 'likes'  # Assign a table name
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    # Define other like fields
    user = db.relationship('MyUser', backref='likes')
    
    post = db.relationship('Post', back_populates='likes')



class Therapist(db.Model):
    
    __tablename__ = 'therapist'
    therapist_id = db.Column(db.Integer, primary_key=True)
    theraname = db.Column(db.String(80), unique=True, nullable=False)
    theraemail = db.Column(db.String(120), unique=True, nullable=False)
    Therapassword = db.Column(db.String(255), nullable=False)
    thera_img=db.Column(db.String(120),nullable=True)
    registration_date2 = db.Column(db.DateTime(), default=datetime.utcnow)
    bio = db.Column(db.String(500), nullable=True)
    specialization = db.Column(db.String(500), nullable=True)

    #   Relationship
    thera= db.relationship("Consultaion", back_populates='feed')
    # consultations = db.relationship('Consultaion', backref='therapist', lazy=True)

    
 


class Response(db.Model):
    __tablename__ = 'response'
    response_id = db.Column(db.Integer, primary_key=True)
    userpostid= db.Column(db.Integer(), db.ForeignKey('post.post_id'),nullable=False)
    user_id= db.Column(db.Integer(), db.ForeignKey('user.userid'),nullable=False)
    response_text = db.Column(db.String(500), nullable=False)
    date_posted= db.Column(db.DateTime(), default=datetime.utcnow)
    post = db.relationship('Post', backref='response')

   
  
    

class Consultaion(db.Model):
    __tablename__ = 'consultation'
    consultation_id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.userid', ondelete='CASCADE'))
    id_therapist = db.Column(db.Integer(), db.ForeignKey('therapist.therapist_id'), nullable=False)
    consultaion_text = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(10), unique=False, nullable=False, server_default='pending')
    booking_time = db.Column(db.DateTime())
    feedback = db.Column(db.String(500), nullable=True)  # Add the feedback column

    #Relationship
    feed= db.relationship("Therapist", back_populates='thera')
    user_feed= db.relationship("MyUser", back_populates='user')
    user = db.relationship('MyUser', backref=db.backref('consultations', cascade='all, delete-orphan'))



    

    # def __init__(self, id_user, id_therapist, consultaion_text, status='pending'):
    #     self.id_user = id_user
    #     self.id_therapist = id_therapist
    #     self.consultaion_text = consultaion_text
    #     self.status = status

  

# class Plan(db.Model):
#     __tablename__ = 'plan'
#     plan_id = db.Column(db.Integer, primary_key=True)
#     plan_name = db.Column(db.String(80), unique=True, nullable=False)
#     plan_sub_month = db.Column(db.String(80), nullable=False)
#     plan_sub_month_price = db.Column(db.String(120))
#     plan_sub_year = db.Column(db.String(80), nullable=False)
#     plan_sub_year_price = db.Column(db.String(120))
#     subscription_id = db.Column(db.Integer(), db.ForeignKey('subscription.subscription_id'), nullable=False)

# class Payment(db.Model):
#     __tablename__ = 'payment'
#     payment_id = db.Column(db.Integer, primary_key=True)
#     user_id= db.Column(db.Integer(), db.ForeignKey('user.userid'),nullable=False)
#     subscription_id = db.Column(db.Integer(), db.ForeignKey('subscription.subscription_id'),nullable=False)
#     amount =  db.Column(db.String(80), nullable=False)
#     payment_date =db.Column(db.DateTime(), default=datetime.utcnow)
#     payment_method= db.Column(db.String(80), nullable=False)

# class Subscription(db.Model):
#     __tablename__ = 'subscription'
#     subscription_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
#     subscription_name = db.Column(db.String(80), nullable=False)
#     description = db.Column(db.String(80), nullable=False)
#     benefits = db.Column(db.String(500), nullable=False)
#     plan_id = db.Column(db.Integer, db.ForeignKey('plan.plan_id'), nullable=False)
#     payment_method = db.Column(db.String(80), nullable=False)
#     plan_start_date = db.Column(db.DateTime, default=datetime.utcnow)
#     plan_end_date = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contactus' 
    contact_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    contact_email = db.Column(db.String(100),nullable=True)
    contact_message = db.Column(db.String(100),nullable=True)

