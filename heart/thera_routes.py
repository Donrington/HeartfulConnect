# import json, os
# from functools import wraps
# from werkzeug.security import generate_password_hash,check_password_hash
# from werkzeug.utils import secure_filename
# from flask import *
# from flask_socketio import SocketIO, emit, join_room, leave_room
# from markupsafe import escape
# import re 
# from flask_wtf.csrf import CSRFProtect
# from heart import app,csrf
# from heart.forms import *
# from heart.models import db,MyUser,Contact,Therapist,Post,Response,Like,Consultaion
# from datetime import datetime

# socketio = SocketIO(app)

# def login_req(f):
#     @wraps(f)  #this ensures that the details(meta data) about the original function f, that is decorated is still available..
#     def login_chk(*args, **kwargs):
#         if session.get("theralogged") !=None:
#             return f(*args,**kwargs)
#         else:
#             flash("Access Denied")
#             return redirect ('/theralogin/')
#     return login_chk




# @app.errorhandler(404)
# def page_not_found(error):
#     id = session.get('theralogged')
#     thera=db.session.query(Therapist).get(id)
#     return render_template ("user/error404.html", thera=thera,error=error, pagename="Home Page"),404


# @app.after_request
# def after_request(response):
#     # To Solve The problem of logged out users details being cache in the brower
#     response.headers["Cache-control"]="no-cache, no-store, must-revalidate"
#     return response

# @app.route('/therareg/', methods=['GET', 'POST'])
# def thera_registration():
#     form = Thera_RegistrationForm()

#     if request.method == 'POST':
#         if form.validate_on_submit():
#             username = request.form.get('username2')
#             email = request.form.get('email2')
#             password = request.form.get('pwd2')
#             specialization = form.specialization2.data  # Get the specialization from the form
            
#             hashed_pwd = generate_password_hash(password)
            
#             user = Therapist(
#                 theraname=username,
#                 theraemail=email,
#                 Therapassword=hashed_pwd,
#                 specialization=specialization  # Assign the specialization field
#             )
            
#             db.session.add(user)
#             db.session.commit()
#             flash(f"{username}, your account has been created successfully.")
#             return redirect('/home/page/')
    
#     return render_template('user/therapistRegForm2.html', pagename="Therapist Registration Page", form=form)

        


# @app.route("/theralogin/", methods=['POST', 'GET'])
# def theraloggin(): # Initialize thera as None
#     form = theralogin()

#     if form.validate_on_submit():
#         username = form.theraname.data
#         password = form.therapwd.data
#         thera = Therapist.query.filter_by(theraname=username).first()

#         if thera is not None and check_password_hash(thera.Therapassword, password):
#             session['theralogged'] = thera.theraname
#             flash('Login successful', 'success')
#             return redirect(url_for('theradashboard'))
#         else:
#             flash('Invalid login. Please try again.', category='danger')

#     return render_template("user/theralogin.html", form=form, thera=thera)  # Pass thera to the template


# @app.route('/theradashboard/')
# def theradashboard():  # Initialize thera with a default value (None in this case)

#     if session.get('theralogged') is not None:
#         thera_id = session.get('theralogged')
#         thera = Therapist.query.get(thera_id)

#         # Fetch other clients excluding the current therapist
#         other_clients = MyUser.query.filter(MyUser.userid != thera_id).all()

#     return render_template('user/theradashboard.html', pagename="Therapist Profile | Heartful Connect", other_clients=other_clients, thera=thera)




# @app.route('/therapist/chat/', methods=['GET', 'POST'])
# def therapist_chat():
#     if 'theralogged' in session:
#         therapist_id = session['theralogged']
#         # Assuming you have a database model for therapists named Therapist
#         therapist = Therapist.query.get(therapist_id)
#         # Initialize user as None

#         if request.method == 'POST':
#             # Extract the message and user_id from the request data
#             data = request.get_json()
#             message = data.get('message')
#             user_id = data.get('user_id')

#             # You may want to validate the message and user_id here

#             # Get the user's information from your database
#             user = MyUser.query.get(user_id)

#             if user:
#                 # Broadcast the message to the user using Socket.IO
#                 room = f'user_{user_id}'  # Use a different room naming convention for users
#                 emit('message', {'message': message, 'sender_id': therapist_id, 'sender_name': therapist.theraname, 'sender_avatar': therapist.thera_img}, room=room)

#                 return jsonify({'success': True, 'message': 'Message sent successfully'})

#         # Render the chat HTML template for GET requests, passing the therapist object
#         return render_template('user/thera_chat.html', therapist=therapist, user=user)

#     return jsonify({'success': False, 'message': 'Therapist not logged in'})





# @app.route("/theraprofileupdate/", methods=['GET', 'POST'])
# def theradp():
#     thera_id = session.get('theralogged')
#     thera = db.session.query(Therapist).get(thera_id)

#     if request.method == 'GET':
#         return render_template("user/therapistprofile.html",thera=thera, thera_id=thera_id)

#     elif request.method == 'POST':
#         pic = request.files.get('dp')

#         if pic:
#             filename = pic.filename
#             pic.save(os.path.join(app.config['THERA_PROFILE_PATH'], filename))
#             thera.thera_img = filename
#             db.session.commit()
#             flash('Profile picture has been updated successfully', category='success')
#             return redirect(url_for('theradashboard'))
#         else:
#             flash('No file selected for upload', category='danger')
#             return redirect(url_for('update_dp'))  # Redirect back to the form
#     return render_template('user/therapistprofile.html', thera=thera, thera_id=thera_id)


# @app.route('/theraprofileupdate/', methods=['POST'])
# def update_dp():
#     if request.method == 'POST':
#         id = session.get('theralogged')
#         thera = Therapist.query.get(id)

#         if thera:
#             # Retrieve the updated information from the form
#             new_email = request.form.get('email')
#             new_password = request.form.get('password')
#             new_phone = request.form.get('phone')
#             bio = request.form.get('bio')
        
#             if new_email:
#                 thera.theraemail = new_email
#             if new_password:
#                 hashed_password = generate_password_hash(new_password)
#                 thera.Therapassword = hashed_password
#             if new_phone:
#                 thera.phone = new_phone
#             if bio:
#                 thera.bio = bio
            
#             # Commit changes to the database
#             db.session.commit()
#             flash('Profile information has been updated successfully', category='success')
#         else:
#             flash('User not found. Please log in again.', category='danger')

#         return redirect(url_for('theradashboard'))
#     return render_template('user/therapistprofile.html', thera=thera)



# @app.route('/thera/consultation/')
# @login_req
# def consults():
#      # Check if the user is logged in (you might have a different way to check this)
#     if 'theralogged' in session:
#         thera_id = session['theralogged']
#         # Assuming you have a database model for users named MyUser
#         thera = Therapist.query.get(thera_id)
#         consultations = db.session.query(MyUser).all()
#     return render_template('user/theraconsultation.html', thera=thera, consultations=consultations, pagename="Consultation | Heartful Connect")






#   # Redirect to the home page or handle as needed
