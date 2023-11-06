import json, os
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask import *
from flask_socketio import SocketIO, emit, join_room, leave_room
from markupsafe import escape
import re 
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from heart import app,csrf
from heart.forms import *
from heart.models import db,MyUser,Contact,Therapist,Post,Response,Like,Consultaion,Admin
from datetime import datetime








# @app.route("/login/",methods=['POST','GET'])
# def lo():
#         if request.method =="GET":
#             return render_template("admin/login.html" ,pagename="Admin login | Heartful Connect")
#         else:
#             username = request.form.get('username')
#             pwd = request.form.get('pwd')
#             if pwd =='1234'and username=="admin":
#                 session['username'] = username
#                 return redirect(url_for("admin_dashboard"))
#             else:
#                  flash('Invalid login Try Again')
#                  return redirect(url_for('login'))


@app.route("/admin/dashboard/")
def admin_dashboard():
    if session.get("Admin") is None:
        flash("You must be logged in to view this page", category="error")
        return render_template("admin/login.html")
    else:
        # Fetch the admin data based on the session's username
        admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()
        
        # Fetch user and therapist data
        users = MyUser.query.all()
        therapists = Therapist.query.all()

        return render_template("admin/dashboard.html", admin=admin, users=users, therapists=therapists)


    # admin logout 
@app.route("/admin/logout/")
def admin_logout():
    if session.get("Admin") != None:
        session.pop("Admin",None)
    return redirect(url_for('admin_login'))



@app.route("/admin/login/",methods=["POST","GET"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/login.html" ,pagename="Admin login | Heartful Connect")
    else:
        username = request.form.get('username')
        pwd = request.form.get("pwd")
        check = db.session.query(Admin).filter(Admin.username==username).first()
        if check != None:
            if pwd == check.password:
                session["Admin"]=username
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid Login Details",category="error")
                return redirect(url_for('login'))
        else:
            flash("Invalid Login Details",category="error")
            return redirect(url_for('login'))



@app.route('/admin/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    # Retrieve the user with the specified user_id
    user = MyUser.query.get_or_404(user_id)

    # Fetch the admin data based on the session's username and pass it to the template
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/view_user.html', user=user, admin=admin)

@app.route('/admin/user', methods=['GET'])
def admin_user():
    # Retrieve a list of all users from the database
    users = MyUser.query.all()

    # Fetch the admin data based on the session's username and pass it to the template
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/users.html', users=users, admin=admin)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Retrieve the user with the specified user_id
    user = MyUser.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update the user's details based on the form data (request.form)
        user.username = request.form['username']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.bio = request.form['bio']
        # Add more fields as needed

        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('admin_user'))

    # Fetch the admin data based on the session's username and pass it to the template
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/edit_user.html', user=user, admin=admin)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Retrieve the user with the specified user_id
    user = MyUser.query.get_or_404(user_id)

    try:
        # Disassociate consultations from the user
        for consultation in user.consultations:
            consultation.id_user = None
        db.session.commit()
    except IntegrityError as e:
        # Handle the IntegrityError (e.g., log the error, show a message)
        db.session.rollback()

    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_user'))







# Import statements and other routes...

@app.route('/admin/view_stories', methods=['GET'])
def admin_view_stories():
    if 'Admin' not in session:
        flash('You must be logged in as an admin to view this page', category='error')
        return redirect(url_for('admin_login'))
    else:
        # Fetch all stories
        stories = Post.query.order_by(Post.post_id.desc()).all()
        admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()
        return render_template('admin/view_stories.html', stories=stories, admin=admin)
        

@app.route('/admin/delete_story/<int:story_id>', methods=['POST', 'GET'])
def admin_delete_story(story_id):
    if 'Admin' not in session:
        flash('You must be logged in as an admin to delete stories', category='error')
        return redirect(url_for('admin_login'))
    else:
        # Retrieve the story with the specified story_id
        story = Post.query.get_or_404(story_id)

        # Delete the story from the database
        db.session.delete(story)
        db.session.commit()

        flash('Story deleted successfully', category='info')
        return redirect(url_for('admin_view_stories'))
    

@app.route('/admin/delete_comment/<int:comment_id>', methods=['POST', 'GET'])
def admin_delete_comment(comment_id):
    if 'Admin' not in session:
        flash('You must be logged in as an admin to delete comments', category='error')
        return redirect(url_for('admin_login'))
    else:
        # Retrieve the comment with the specified comment_id
        comment = Response.query.get_or_404(comment_id)

        # Delete the comment from the database
        db.session.delete(comment)
        db.session.commit()

        flash('Comment deleted successfully', category='info')
        return redirect(url_for('admin_view_stories'))






@app.route('/admin/view_therapist/<int:therapist_id>', methods=['GET'])
def view_therapist(therapist_id):
    # Retrieve the therapist with the specified therapist_id
    therapist = Therapist.query.get_or_404(therapist_id)

    # Fetch the admin data based on the session's username and pass it to the template
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/therapist_view.html', therapist=therapist, admin=admin)

@app.route('/admin/edit_therapist/<int:therapist_id>', methods=['GET', 'POST'])
def edit_therapist(therapist_id):
    # Retrieve the therapist with the specified therapist_id
    therapist = Therapist.query.get_or_404(therapist_id)

    if request.method == 'POST':
        # Update the therapist's details based on the form data (request.form)
        therapist.theraname = request.form['theraname']
        therapist.theraemail = request.form['theraemail']
        therapist.specialization = request.form['specialization']
        therapist.bio = request.form['bio']
        # Add more fields as needed

        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # Fetch the admin data based on the session's username and pass it to the template
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/therapist_edit.html', therapist=therapist, admin=admin)

@app.route('/admin/delete_therapist/<int:therapist_id>', methods=['POST'])
def delete_therapist(therapist_id):
    # Retrieve the therapist with the specified therapist_id
    therapist = Therapist.query.get_or_404(therapist_id)

    # Delete the therapist from the database
    db.session.delete(therapist)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/thera', methods=['GET'])
def admin_thera():
    # Retrieve a list of all users from the database
    therapist = Therapist.query.all()
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()

    return render_template('admin/therapist.html', therapist=therapist, admin=admin)



@app.route('/get_user_therapist_data', methods=['GET'])
def get_user_therapist_data():
   
    user_count = MyUser.query.count()
    therapist_count = Therapist.query.count()

    # Return the data as JSON
    data = {
        "userData": [user_count] * 7,  # Assuming 7 days in a week
        "therapistData": [therapist_count] * 7  # Assuming 7 days in a week
    }
    return jsonify(data)


@app.route('/admin/consultations', methods=['GET'])
def admin_consultations():
    if 'Admin' not in session:
        flash('You must be logged in as an admin to view consultations', category='error')
        return redirect(url_for('admin_login'))
    else:
        # Fetch all consultations
        consultations = Consultaion.query.all()
        admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()
        return render_template('admin/consultations.html', consultations=consultations, admin=admin)
    


@app.route('/admin/delete_consultation/<int:consultation_id>', methods=['POST'])
def admin_delete_consultation(consultation_id):
    if 'Admin' not in session:
        flash('You must be logged in as an admin to delete consultations', category='error')
        return redirect(url_for('admin_login'))
    else:
        # Retrieve the consultation with the specified consultation_id
        consultation = Consultaion.query.get_or_404(consultation_id)

        # Delete the consultation from the database
        db.session.delete(consultation)
        db.session.commit()

        flash('Consultation deleted successfully', category='info')
        return redirect(url_for('admin_consultations'))



@app.route('/admin/change_profile_picture', methods=['GET', 'POST'])
def admin_change_profile_picture():
    if 'Admin' not in session:
        flash('You must be logged in as an admin to change your profile picture', category='error')
        return redirect(url_for('admin_login'))
    
    admin = db.session.query(Admin).filter(Admin.username == session.get("Admin")).first()
    
    if request.method == 'POST':
        # Check if a file is provided
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            
            # Save the uploaded profile picture
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['ADMIN_PROFILE_PATH'], filename))
                admin.admin_img = filename
                db.session.commit()
                flash('Profile picture updated successfully', category='success')
                return redirect(url_for('admin_change_profile_picture'))
    
    return render_template('admin/admin_profile.html', admin=admin)
