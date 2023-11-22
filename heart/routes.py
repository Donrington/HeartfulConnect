import json, os
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask import * 
from flask_socketio import SocketIO, emit, join_room, leave_room
from markupsafe import escape
import re 
from flask_wtf.csrf import CSRFProtect
from heart import app,csrf,socketio
from heart.forms import *
from heart.models import db,MyUser,Contact,Therapist,Post,Response,Like,Consultaion,Chat
from heart.forms import ConsultationForm
from sqlalchemy import func
from datetime import datetime




user_bp = Blueprint('user', __name__)


socketio = SocketIO(app)


@socketio.on('message')
def handle_message(data):
    message = data['message']
    therapist_id = data['therapist_id']
    room = f'therapist_{therapist_id}'
    emit('message', {'message': message}, room=room)\


@user_bp.route('/story/get-message-count', methods=['GET'])
def get_message_count():
    if 'userlogged' in session:
        user_id = session['userlogged']
        message_count = db.session.query(func.count(Like.like_id)).filter(Like.story_id == Post.post_id, Like.user_id == user_id).scalar()
        app.logger.info(f"Message count: {message_count}")
        return jsonify({'count': message_count})
    app.logger.warning("User not logged in.")
    return jsonify({'count': 0})




def login_required(f):
    @wraps(f)  #this ensures that the details(meta data) about the original function f, that is decorated is still available..
    def login_check(*args, **kwargs):
        if session.get("userlogged") !=None:
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect (url_for('user.login'))
    return login_check

@user_bp.route('/user/chat/', methods=['GET', 'POST'])
def user_chat():
    if 'userlogged' in session:
        user_id = session['userlogged']
        user = MyUser.query.get(user_id)
        therapist_id = None  # Initialize therapist_id as None

        if request.method == 'POST':
            data = request.get_json()
            message = data.get('message')
            therapist_id = data.get('therapist_id')

            therapist = Therapist.query.get(therapist_id)

            if therapist:
                room = f'user_{user_id}' 
                emit('message', {'message': message, 'sender_id': user_id, 'sender_name': user.username, 'sender_avatar': user.user_img}, room=room)

                # Create a new Chat object and add it to the database
                new_chat = Chat(
                    message=message,
                    sender_id=user_id,
                    sender_name=user.username,
                    sender_avatar=user.user_img,
                    user_id=user_id,
                    therapist_id=therapist_id
                )
                db.session.add(new_chat)
                db.session.commit()

                return jsonify({'success': True, 'message': 'Message sent successfully'})

        # Query chat messages from the database for the user
        user_chats = Chat.query.filter_by(user_id=user_id).all()

        return render_template('user/chat.html', user=user, therapist_id=therapist_id, user_chats=user_chats)

    return jsonify({'success': False, 'message': 'User not logged in'})





# @user_bp.route('/user/consultation/', methods=['GET', 'POST'])
# @login_required
# def consult():
#     form = ConsultationForm()  # Create an instance of the form

#     if form.validate_on_submit():
#         # Form has been submitted and validated
#         message = form.message.data

#         # Get the user ID from the session
#         user_id = session.get('userlogged')

#         if user_id is not None:
#             # Create a new consultation and add it to the database
#             therapist_id = 1  # Replace with the actual therapist's ID
#             therapist = Therapist.query.get(therapist_id)

#             new_consultation = Consultaion(id_user=user_id, id_therapist=therapist_id, consultaion_text=message, booking_time=datetime.now())
#             db.session.add(new_consultation)
#             db.session.commit()

#             flash('Your consultation request has been submitted.', 'success')
#             return redirect(url_for('user.consult'))  # Redirect to the consultation page after submission
#         else:
#             flash('User ID not found. Please log in.', 'danger')

#     # Retrieve the user's consultations
#     user_id = session.get('userlogged')
#     user = MyUser.query.get(user_id)

#     # Retrieve all therapists and their associated consultations
#     therapists = Therapist.query.all()
#     consultation = Consultaion.query.filter_by(id_user=user_id).all()

#     return render_template('user/consultation.html', user=user, therapists=therapists, consultation=consultation, form=form, pagename="Consultation | Heartful Connect")





@user_bp.route('/user/consultation/', methods=['GET', 'POST'])
def consult():
    form = ConsultationForm()  # Create an instance of the form

    if form.validate_on_submit():
        # Form has been submitted and validated
        message = form.message.data

        # Get the user ID from the session
        user_id = session.get('userlogged')

        if user_id is not None:
            # Check if the user has selected a therapist; you may use a form field for this
            selected_therapist_id = request.form.get('therapist_id')
            
            # Get the date components from the form
            day = int(request.form.get('day'))
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))
            hour = int(request.form.get('hour'))
            minute = int(request.form.get('minute'))

            # Create a date object from the components
            consultation_date = datetime(year, month, day, hour, minute)

            if selected_therapist_id is not None:
                # Create a new consultation and add it to the database
                new_consultation = Consultaion(
                    id_user=user_id,
                    id_therapist=selected_therapist_id,
                    consultaion_text=message,
                    booking_time=consultation_date  # Save the date to the database
                )
                db.session.add(new_consultation)
                db.session.commit()

                flash('Your consultation request has been submitted.', 'success')
                return redirect(url_for('user.consult'))  # Redirect to the consultation page after submission
            else:
                flash('Please select a therapist.', 'danger')
        else:
            flash('User ID not found. Please log in.', 'danger')

    # Retrieve the user's consultations
    user_id = session.get('userlogged')
    user = MyUser.query.get(user_id)

    # Retrieve all therapists
    therapists = Therapist.query.all()

    # Retrieve consultations for the logged-in user
    consultation = Consultaion.query.filter_by(id_user=user_id).all()

    return render_template('user/consultation.html', user=user, therapists=therapists, consultations=consultation, form=form, pagename="Consultation | Heartful Connect")


@user_bp.route('/user/submit_consultation/<int:therapist_id>', methods=['POST'])
def submit_consultation(therapist_id):
    user_id = session.get('userlogged')
    # Get the message from the form data
    message = request.form.get('message')

    day = int(request.form.get('day'))
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    hour = int(request.form.get('hour'))
    minute = int(request.form.get('minute'))
    # Create a date object from the components
    consultation_date = datetime(year, month, day,hour,minute)

    if message:
        # Assuming you have a Consultation model
        new_consultation = Consultaion(
            id_user=user_id,
            id_therapist=therapist_id,
            consultaion_text=message,
            booking_time=consultation_date
        )
        db.session.add(new_consultation)
        db.session.commit()

        flash("Message has been sent succesfully")
        return redirect(url_for('user.consult'))
    else:
        flash("An invalid message, Kindly input the correct one")
        return redirect(url_for('user.consult'))









@user_bp.errorhandler(404)
def user_page_not_found(error):
    id = session.get('userlogged')
    user=db.session.query(MyUser).get(id)
    return render_template ("user/error404.html", user=user,error=error, pagename="Home Page"),404




@user_bp.errorhandler(404)
def user_page_not_found(error):
    id = session.get('userlogged')
    feed = db.session.query(Consultaion).all()
    return render_template("user/consultation.html",feed=feed)






@user_bp.after_request
def after_request(response):
    # To Solve The problem of logged out users details being cache in the brower
    response.headers["Cache-control"]="no-cache, no-store, must-revalidate"
    return response


@user_bp.route('/comingsoon/')
def comingsoon():
    id = session.get('userlogged')
    user=db.session.query(MyUser).get(id)
    return render_template ("user/comingsoon.html", user=user, pagename="Coming Soon to Heartful Connect")

@user_bp.route("/user/home/page/")
def userhomepage():
    id = session.get('userlogged')
    user=db.session.query(MyUser).get(id)
    config_items = app.config
    return render_template("user/index_new.html", pagename="Home Page",user=user, config_items=config_items)



@user_bp.route('/userreg/', methods=['GET','POST'])
def User_registration():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('user/userRegForm2.html', pagename="User Registration Page", form=form)
    else:
        if form.validate_on_submit():
            username = request.form.get('username')
            email = request.form.get('usermail')
            password = request.form.get('pwd')
            phone=request.form.get('userphone')
            hashed_pwd=generate_password_hash(password)
            user=MyUser(username=username,email=email,password=hashed_pwd,phone=phone)
            db.session.add(user)
            db.session.commit()
            flash(f"{username} Your account has been created Succesfully..")
            return redirect(url_for('user.userhomepage'))
        else:
            return render_template('user/userRegForm2.html',form=form)



@user_bp.route('/user/profile/update', methods=['POST', 'GET'])
def update_profile():
    user_id = session.get('userlogged')
    user = MyUser.query.get(user_id)

    if request.method == 'GET':
        return render_template('user/profile.html', user=user)

    elif request.method == 'POST':
        new_email = request.form.get('email')
        bio = request.form.get('bio')
        new_password = request.form.get('password')
        phone = request.form.get('phone')
        profile_picture = request.files.get('profile_picture')
        # Update the user's email, bio, and password if provided
        if new_email:
            user.email = new_email
        if bio:
            user.bio = bio
        if phone:
            user.phone = phone
        if new_password:
            new_password_hashed = generate_password_hash(new_password)
            user.password = new_password_hashed

        # Handle profile picture upload
       
        if profile_picture:
            filename = profile_picture.filename
            profile_picture.save(os.path.join(app.config['USER_PROFILE_PATH'], filename))
            user.user_img = filename

        db.session.commit()
        flash('Profile information has been updated successfully', category='success')
        return redirect(url_for('user.dashboard'))

    flash('User not found. Please log in again.', category='danger')
    return render_template('user/profile.html', user=user)


@user_bp.route('/user/logout/')
def logout():
    user = None  # Initialize user as None

    if session.get('userlogged') is not None:
        user = session.get('userlogged')
        # Assuming you have a database model for users named MyUser
        user = MyUser.query.get(user)

        session.pop('userlogged', None)
        flash('You have been logged out', category='success')

    return redirect(url_for('user.userhomepage'))


@user_bp.route("/userlogin/", methods=['POST', 'GET'])
def login():
    form = userlogin()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = MyUser.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            session['userlogged'] = user.userid
             # Set the session variable
            flash('Login successful', category='success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid login. Please try again.', category='danger')

    return render_template("user/loginForm.html", form=form)






@user_bp.route("/dashboard/")
def dashboard():
    if session.get('userlogged') is not None:
        id = session.get('userlogged')
        user = MyUser.query.get(id)
        #fetch the consultation details and put it here.
        other_users = MyUser.query.filter(MyUser.userid != id).all()
        # Fetch the stories for the dashboard
        stories = Post.query.order_by(Post.post_id.desc()).all()

        if 'userlogged' in session:
            user_id = session['userlogged']
        for story in stories:
            story.has_liked = story.has_liked(user_id)
        
        return render_template('user/dashboard_new.html', user=user,  other_users= other_users,stories=stories, pagename="Dashboard | Heartful Connect")
    else:
        flash('You need to login to access the page')
        return redirect("/userlogin/")
    


@user_bp.route('/search', methods=['POST', 'GET'])
def search():
    search_query = request.form.get('search_query')

    # Implement the search logic here, query users and therapists based on the search query
    # For example:
    users = MyUser.query.filter(MyUser.username.ilike(f'%{search_query}%')).all()
    therapists = Therapist.query.filter(Therapist.theraname.ilike(f'%{search_query}%')).all()

    # Prepare the search results as a list of dictionaries
    search_results = []

    # Add search results to the list
    for user in users:
        search_results.append({'type': 'user', 'name': user.username, 'link': url_for('user.user_profile', user_id=user.userid)})

    for therapist in therapists:
        search_results.append({'type': 'therapist', 'name': therapist.theraname, 'link': url_for('therapist.thera_profile', thera_id=therapist.therapist_id)})

    return jsonify(search_results=search_results)













@user_bp.route('/story/', methods=['GET', 'POST'])
@csrf.exempt
def userstory():
    if 'userlogged' in session:
            user_id = session['userlogged']
            user = MyUser.query.get(user_id)
    if request.method == 'POST':
        # Handle story posting
        content = request.form.get('story_content')
        if content:
                new_story = Post(user_id=user_id, content=content, post_time=datetime.now().time())
                db.session.add(new_story)
                db.session.commit()
                flash('Post has been successfully added', category='info')

            # Return JSON response for AJAX request
        return jsonify({'status': 'success', 'message': 'Story posted successfully'})

    # Order stories by the latest post in descending order
    stories = Post.query.order_by(Post.post_id.desc()).all()
    stories = stories[::1]
    
    # Determine if the current user has liked each story
    if 'userlogged' in session:
        user_id = session['userlogged']
        for story in stories:
            story.has_liked = story.has_liked(user_id)
    
    return render_template('user/story.html', stories=stories, user=user, pagename="Story | Heartful Connect")




@user_bp.route('/post/comment/<int:story_id>', methods=['POST'])
@login_required
def post_comment(story_id):
    print("Route accessed") 
    # Get the user ID from the session
    user_id = session.get('userlogged')
    
    # Get the comment content from the form
    comment_content = request.form.get('comment_content')
    
    # Create a new comment and add it to the database
    new_comment = Response(user_id=user_id, userpostid=story_id, response_text=comment_content)
    db.session.add(new_comment)
    db.session.commit()
    
    flash('Your comment has been posted.', 'success')
    
    return redirect(url_for('user.userstory'))  # Redirect to the story page


@user_bp.route('/post/like/<int:story_id>', methods=['POST','GET'])
@login_required
def like_post(story_id):
    # Get the user ID from the session
    user_id = session.get('userlogged')
    
    # Check if the user has already liked the post
    post = Post.query.get(story_id)
    if post.has_liked(user_id):
        flash('You have already liked this post.', 'warning')
    else:
        # Create a new like and add it to the database
        new_like = Like(user_id=user_id, story_id=story_id)
        db.session.add(new_like)
        db.session.commit()
        flash('You liked the post.', 'success')
    
    return jsonify({'status': 'success', 'message': 'You liked the post', 'liked': True})

@user_bp.route('/post/unlike/<int:story_id>', methods=['POST','GET'])
@login_required
def unlike_post(story_id):
    # Get the user ID from the session
    user_id = session.get('userlogged')
    
    # Check if the user has liked the post
    post = Post.query.get(story_id)
    like = Like.query.filter_by(user_id=user_id, story_id=story_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash('You unliked the post.', 'success')
        return jsonify({'status': 'success', 'message': 'You unliked the post', 'liked': False})
    else:
        flash('You cannot unlike a post you have not liked.', 'warning')
        return jsonify({'status': 'success', 'message': 'You cannot unlike a post you have not liked', 'liked': True})















@user_bp.route('/user_profile/')
# Use the login_required decorator to protect this route
def user_profile():
    if 'userlogged' in session:
        user_id = session['userlogged']
        # Fetch user data from the database using user_id (assuming you have a User model)
        user = db.session.query(MyUser).get(user_id)
        
        if user:
            return render_template('user/userprofile.html', user=user)
        else:
            # Handle the case where the user is not found
            flash('User not found.', category='danger')
            return redirect(url_for('user.userhomepage'))
    else:
        # Handle the case where the user is not logged in
        flash('Please log in to access your profile.', category='danger')
        return redirect(url_for('user.userhomepage'))







@user_bp.route('/userprofile/')
def userprofile():
        id = session.get('userlogged')
        user=db.session.query(MyUser).get_or_404(id)
            
        return render_template('user/profile.html', user=user,user_id=id)
       

@app.route('/')
def index_front():
    return render_template('user/index2.html', pagename="Welcome Page | Heartful Connect")



@user_bp.route('/submitcontact/', methods=['POST','GET'])
def submit_contact():
    if request.method == 'POST':
        # Retrieve form data from the request
        email = request.form.get('Email')
        message = request.form.get('Message')

        # Create a new Contact instance
        new_contact = Contact(contact_email=email, contact_message=message)

        # Add the new Contact instance to the database session
        db.session.add(new_contact)

        # Commit the changes to the database
        db.session.commit()
        flash(f'Thank you {email}, your message was recieved',category='Success')
        flash(f"We will get back to you within 24 hours..",category='Success')
        # Redirect to the homepage (you can replace 'home' with your actual homepage route)
        return redirect(url_for('user.userhomepage'))







@user_bp.route('/view_therapist_profile/<int:thera_id>')
@login_required
def view_therapist_profile(thera_id):
    # Fetch user data from the database using user_id (assuming you have a User model)
    thera = db.session.query(Therapist).get(thera_id)

    # Retrieve therapist session information
    user_id = session.get('userlogged')
    user = db.session.query(MyUser).get(user_id)

    if thera:
        if user:
            # If a therapist is logged in, render a therapist-specific template
            return render_template('user/view_therapist_profile.html', user=user, thera=thera)
        else:
            # If a regular user is logged in, render the regular user template
            return render_template('user/theraprofile2.html', thera=thera)
    else:
        # Handle the case where the user is not found
        flash('User not found.', category='danger')
        return redirect(url_for('user.consult'))


























# ################################################ Therapist ################################################################


therapist_bp = Blueprint('therapist', __name__)




@socketio.on('message')
def thera_handle_message(data):
    message = data['message']
    user_id = data['user_id']  # Assume user_id is included in the message data
    room = f'user_{user_id}'  # Use a different room naming convention for users
    emit('message', {'message': message}, room=room)






@therapist_bp.route('/therapist/profile/')
def theraprofile():
    if session.get('theralogged') is not None:
        thera_id = session.get('theralogged')
        thera = Therapist.query.filter_by(theraname=thera_id).first()

        user = None  # Initialize user as None
        if 'userlogged' in session:
            user_id = session.get('userlogged')
            # Assuming you have a database model for users named MyUser
            user = MyUser.query.get(user_id)

        return render_template('user/theraprofile.html', thera=thera, user=user, pagename="Therapist Profile | Heartful Connect")

    # Add a response for the case where 'theralogged' is not in the session or is None
    # For example, you could redirect the user to a login page or display an error message.
    # Replace the following line with the desired behavior:
    return "You are not logged in as a therapist."



@therapist_bp.route("/thera/home/page/")
def therahomepage():
    id = session.get('theralogged')
    thera=db.session.query(Therapist).get(id)
    config_items = app.config
    return render_template("user/index_thera.html", pagename="Home Page",thera=thera, config_items=config_items)


@therapist_bp.route('/thera/logout/')
def theralogout():
    thera = None  # Initialize user as None

    if session.get('theralogged') is not None:
        thera = session.get('theralogged')
        # Assuming you have a database model for users named MyUser
        thera = Therapist.query.get(thera)

        session.pop('theralogged', None)
        flash('You have been logged out', category='success')

    return redirect(url_for('therapist.therahomepage'))



@therapist_bp.route('/therareg/', methods=['GET','POST'])
def thera_registration():
    form = Thera_RegistrationForm()
    if request.method == 'GET':
        return render_template('user/therapistRegForm2.html', pagename="Therapist Registration Page", form=form)
    else:
        if form.validate_on_submit():
            username = request.form.get('username2')
            email = request.form.get('email2')
            password = request.form.get('pwd2')
            hashed_pwd=generate_password_hash(password)
            specialization = form.specialization2.data 
            user=Therapist(theraname=username,theraemail=email,Therapassword=hashed_pwd, specialization=specialization)
            db.session.add(user)
            db.session.commit()
            flash(f"{username} Your account has been created Succesfully..")
            return redirect(url_for('therapist.therahomepage'))
        else:
            return render_template('user/therapistRegForm2.html',form=form)
        


@therapist_bp.route('/theradashboard/')
def theradashboard():
    thera_id = session.get('theralogged')  # Retrieve the therapist's ID from the session

    if thera_id is not None:  # Check if a therapist is logged in
        thera = Therapist.query.get(thera_id)  # Query the therapist by ID

        if thera is not None:  # Check if the therapist exists
            # Fetch other clients excluding the current therapist
            other_clients = MyUser.query.filter(MyUser.userid != thera_id).all()
    
            # Assuming you have a Consultation model for consultations
            consultations = Consultaion.query.filter(Consultaion.id_therapist == thera_id).all()

            return render_template('user/theradashboard.html', pagename="Therapist Profile | Heartful Connect", other_clients=other_clients, thera=thera, consultations=consultations)
        else:
            flash('Therapist not found. Please log in again.', category='danger')
            return redirect(url_for('therapist.theraloggin'))
    else:
        # Handle the case where the therapist is not logged in (you can redirect or display an error)
        flash('Please log in as a therapist to access this page.', category='danger')
        return redirect(url_for('therapist.theraloggin'))






@therapist_bp.route("/theraprofileupdate/", methods=['GET', 'POST'])
def update_dp():
    thera_id = session.get('theralogged')
    thera = db.session.query(Therapist).get(thera_id)

    if request.method == 'POST':
        # Check if a picture file is part of the form
        pic = request.files.get('dp')

        # Retrieve the updated information from the form
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        new_phone = request.form.get('phone')
        bio = request.form.get('bio')

        if thera:
            if pic:
                filename = pic.filename
                pic.save(os.path.join(app.config['THERA_PROFILE_PATH'], filename))
                thera.thera_img = filename

            if new_email:
                thera.theraemail = new_email
            if new_password:
                hashed_password = generate_password_hash(new_password)
                thera.Therapassword = hashed_password
            if new_phone:
                thera.phone = new_phone
            if bio:
                thera.bio = bio

            # Commit changes to the database
            db.session.commit()
            thera = db.session.query(Therapist).get(thera_id)
            flash('Profile information has been updated successfully', category='success')
        else:
            flash('User not found. Please log in again.', category='danger')

        return redirect(url_for('therapist.theradashboard'))

    return render_template("user/therapistprofile.html", thera=thera, thera_id=thera_id)


@therapist_bp.route('/therapist/therachat/', methods=['GET', 'POST'])
def therapist_chat():
    if 'theralogged' in session:
        therapist_id = session['theralogged']
        therapist = Therapist.query.get(therapist_id)
        user = None 

        if request.method == 'POST':
            data = request.get_json()
            message = data.get('message')
            user_id = data.get('user_id')

            user = MyUser.query.get(user_id)

            if user and therapist_id:
                # Create a new Chat object and add it to the database
                new_chat = Chat(
                    message=message,
                    sender_id=therapist_id,
                    sender_name=therapist.theraname,
                    sender_avatar=therapist.thera_img,
                    user_id=user_id,
                    therapist_id=therapist_id
                )
                db.session.add(new_chat)
                db.session.commit()

                room = f'user_{user_id}' 
                emit('message', {'message': message, 'sender_id': therapist_id, 'sender_name': therapist.theraname, 'sender_avatar': therapist.thera_img}, room=room)

                return jsonify({'success': True, 'message': 'Message sent successfully'})

        # Query chat messages from the database for the therapist
        therapist_chats = Chat.query.filter_by(therapist_id=therapist_id).all()

        return render_template('user/thera_chat.html', therapist=therapist, user=user, therapist_chats=therapist_chats)

    return jsonify({'success': False, 'message': 'Therapist not logged in'})



def login_req(f):
    @wraps(f)  #this ensures that the details(meta data) about the original function f, that is decorated is still available..
    def login_chk(*args, **kwargs):
        if session.get("theralogged") !=None:
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect ('/theralogin/')
    return login_chk




@therapist_bp.errorhandler(404)
def thera_page_not_found(error):
    id = session.get('theralogged')
    thera=db.session.query(Therapist).get(id)
    return render_template ("user/error404.html", thera=thera,error=error, pagename="Home Page"),404



@therapist_bp.route("/theralogin/", methods=['POST', 'GET'])
def theraloggin():
    form = theralogin()  # Create an instance of the theralogin form

    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.theraname.data
        password = form.therapwd.data
        thera = Therapist.query.filter_by(theraname=username).first()

        if thera is not None and check_password_hash(thera.Therapassword, password):
            session['theralogged'] = thera.therapist_id  # Store the therapist's ID in the session
            flash('Login successful', 'success')
            return redirect(url_for('therapist.theradashboard'))
        else:
            flash('Invalid login. Please try again.', category='danger')

    return render_template("user/theralogin.html", form=form)





@therapist_bp.route('/thera/consultation/')
def consults():
    # Check if the therapist is logged in
    if 'theralogged' in session:
        thera_id = session['theralogged']
        # Assuming you have a database model for therapists named Therapist
        thera = Therapist.query.get(thera_id)

        # Query pending consultations for the therapist
        pending_consultations = Consultaion.query.filter(Consultaion.id_therapist == thera_id).all()

        return render_template('user/theraconsultation.html', thera=thera, pending_consultations=pending_consultations, pagename="Consultation | Heartful Connect")
    else:
        flash('Therapist not logged in.', category='danger')
        return redirect(url_for('therapist.theralogin'))
    

@therapist_bp.route('/view_user_profile/<int:user_id>')
@login_req
def view_user_profile(user_id):
    # Fetch user data from the database using user_id (assuming you have a User model)
    user = db.session.query(MyUser).get(user_id)

    # Retrieve therapist session information
    thera_id = session.get('theralogged')
    thera = db.session.query(Therapist).get(thera_id)

    if user:
        if thera:
            # If a therapist is logged in, render a therapist-specific template
            return render_template('user/view_user_profile.html', user=user, thera=thera)
        else:
            # If a regular user is logged in, render the regular user template
            return render_template('user/userprofile.html', user=user)
    else:
        # Handle the case where the user is not found
        flash('User not found.', category='danger')
        return redirect(url_for('therapist.consults'))





@therapist_bp.route('/thera_profile/')
# Use the login_required decorator to protect this route
def thera_profile():
    user = None
    if 'theralogged' in session:
        thera_id = session['theralogged']
        # Fetch user data from the database using user_id (assuming you have a User model)
        thera = db.session.query(Therapist).get(thera_id)
        
        if thera:
            return render_template('user/theraprofile2.html', thera=thera, user=user)
        else:
            # Handle the case where the user is not found
            flash('User not found.', category='danger')
            return redirect(url_for('therapist.userhomepage'))
    else:
        # Handle the case where the user is not logged in
        flash('Please log in to access your profile.', category='danger')
        return redirect(url_for('therapist.therahomepage'))




@therapist_bp.route('/accept_consultation/<int:consultation_id>', methods=['GET'])
def accept_consultation(consultation_id):
    consultation = Consultaion.query.get(consultation_id)
    
    if consultation:
        # Mark the consultation as 'accepted' in the database
        consultation.status='accepted'
        db.session.commit()

        # Redirect to the user's chat route
        return redirect(url_for('therapist.consults', user_id=consultation.id_user))
    else:
        flash('Consultation not found.', category='danger')
        return redirect(url_for('therapist.theradashboard'))


@app.route('/submit_feedback/<int:consultation_id>', methods=['POST'])
def submit_feedback(consultation_id):
    feedback = request.json.get('feedback')

    # Assuming you have a Consultaion model
    consultation = Consultaion.query.get(consultation_id)
    
    if consultation:
        consultation.feedback = feedback
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 404


@therapist_bp.route('/decline_consultation/<int:consultation_id>')
@login_req
def decline_consultation(consultation_id):
    consultation = Consultaion.query.get(consultation_id)
    if consultation:
        consultation.status = 'declined'
        feedback = 'Declined'  # Provide default feedback for decline or modify as needed
        consultation.consultaion_text = feedback
        db.session.commit()
        flash("The appointment has been Declined", category='danger')
    return redirect('/therapist/consultation/')




@therapist_bp.route('/submitcontact/', methods=['POST','GET'])
def submitcontact():
    if request.method == 'POST':
        # Retrieve form data from the request
        email = request.form.get('Email')
        message = request.form.get('Message')

        # Create a new Contact instance
        new_contact = Contact(contact_email=email, contact_message=message)

        # Add the new Contact instance to the database session
        db.session.add(new_contact)

        # Commit the changes to the database
        db.session.commit()
        flash(f'Thank you {email}, your message was recieved',category='Success')
        flash(f"We will get back to you within 24 hours..",category='Success')
        # Redirect to the homepage (you can replace 'home' with your actual homepage route)
        return redirect(url_for('user.userhomepage'))
    

@therapist_bp.after_request
def afterrequest(response):
    # To Solve The problem of logged out users details being cache in the brower
    response.headers["Cache-control"]="no-cache, no-store, must-revalidate"
    return response



@therapist_bp.route('/search', methods=['POST','GET'])
def search():
    search_query = request.form.get('search_query')

    # Implement the search logic here, query users and therapists based on the search query
    # For example:
    users = MyUser.query.filter(MyUser.username.ilike(f'%{search_query}%')).all()
    therapists = Therapist.query.filter(Therapist.theraname.ilike(f'%{search_query}%')).all()

    # Prepare the search results as a list of dictionaries
    search_results = []

    # Add search results to the list
    for user in users:
        search_results.append({'type': 'user', 'name': user.username, 'link': url_for('user.user_profile', user_id=user.userid)})

    for therapist in therapists:
        search_results.append({'type': 'therapist', 'name': therapist.theraname, 'link': url_for('therapist.thera_profile', thera_id=therapist.therapist_id)})

    return jsonify(search_results=search_results)
