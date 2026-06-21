#App routes
from flask import Blueprint, Flask,render_template,request,url_for,redirect
from .models import *
#from flask import current_app as app
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/")
def home():
    return render_template("home.html")


@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=Users.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return redirect(url_for("admin_dashboard",name=uname))
        elif usr and usr.role==1: #Existed and normal user
            return redirect(url_for("user_dashboard",name=uname,id=usr.id))
        elif usr and usr.role==2: #Existed and Staff user
            return redirect(url_for("staff_dashboard",name=uname,id=usr.id))
        else:
            return render_template("login.html",msg="Invalid user credentials...")

    return render_template("login.html",msg="")


@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=Users.query.filter_by(email=uname).first()
        if usr:
            return render_template("register.html",msg="Sorry, this mail already registered!!!")
        new_usr=Users(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("register.html",msg="")




