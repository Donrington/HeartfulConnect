import json, os
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask import *
from flask_socketio import SocketIO, emit, join_room, leave_room
from markupsafe import escape
import re 
from flask_wtf.csrf import CSRFProtect
from heart import app,csrf
from heart.forms import *
from heart.models import db,MyUser,Contact,Therapist,Post,Response,Like,Consultaion
from datetime import datetime











    


# @app.route("/login/", methods=['POST', 'GET'])
# @csrf.exempt
# def login():
#     if request.method == "GET":
#         return render_template("user/loginForm.html", pagename="Login Page")
#     else:
#         username = request.form.get("username")
#         pwd = request.form.get('pwd')
#         password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'

#         if re.match(password_pattern, pwd):
#             # Password meets the criteria
#             session['username'] = username
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid Login. Please try again with a valid password.')
#             return redirect('/login/')

                
        





# @app.route("/login/",methods=['POST','GET'])
# def loginthera():
#         if request.method =="GET":
#             return render_template("user/loginForm.html")
#         else:
#             username2 = request.form.get('username2')
#             pwd = request.form.get('pwd2')
#             if pwd =='1234':
#                 session['username2'] = username2
#                 return redirect("/dashboard/")
#             else:
#                  flash('Invalid login Try Again')
#                  return redirect('/login/')




        















  




