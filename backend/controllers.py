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
        uname=request.form.get("username")
        pwd=request.form.get("password")
        usr=Users.query.filter_by(username=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return redirect(url_for("auth.admin_dashboard",name=uname))
        elif usr and usr.role==1: #Existed and normal user
            return redirect(url_for("auth.user_dashboard",name=uname,id=usr.id))
        elif usr and usr.role==2: #Existed and Staff user
            return redirect(url_for("auth.staff_dashboard",name=uname,id=usr.id))
        else:
            return render_template("login.html",msg="Invalid user credentials...")

    return render_template("login.html",msg="")


@auth_bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        uname=request.form.get("username")
        pwd=request.form.get("password")
        email=request.form.get("email")
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=Users.query.filter_by(username=uname).first()
        if usr:
            return render_template("register.html",msg="Sorry, this mail already registered!!!")
        new_usr=Users(username=uname,email=email,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("register.html",msg="")

@auth_bp.route("/admin_dashboard")
def admin_dashboard():
    name=request.args.get("name")
    return render_template("admin_dashboard.html", name=name)

@auth_bp.route("/user_dashboard")
def user_dashboard():
    name=request.args.get("name")
    return render_template("user_dashboard.html", name=name)

@auth_bp.route("/staff_dashboard")
def staff_dashboard():
    name=request.args.get("name")
    return render_template("staff_dashboard.html", name=name)


