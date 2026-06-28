#App routes
from flask import Blueprint, Flask,render_template,request,url_for,redirect,flash ,session 
from .models import *
from datetime import datetime
#from flask import current_app as app
auth_bp = Blueprint('auth', __name__)

ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}

@auth_bp.route("/")
def home():
    return render_template("home.html")


@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        uname=request.form.get("username")
        pwd=request.form.get("password")

        if uname == ADMIN_CREDENTIALS['username'] and pwd == ADMIN_CREDENTIALS['password']:
                session.clear()
                session['username'] = uname
                session['role'] = 'admin'
                return redirect(url_for('auth.admin_dashboard'))

        usr=Users.query.filter_by(username=uname,password=pwd).first()

        if usr and usr.role==1: #Existed and normal user
            session.clear()
            session['username'] = usr.username
            session['role'] = 'user'
            return redirect(url_for("auth.user_dashboard",name=uname,id=usr.id))
        
        elif usr and usr.role == 2:  # Staff
            if not usr.is_approved:
                return render_template("login.html", msg="Your account is pending admin approval.")
            session.clear()
            session['username'] = usr.username
            session['role'] = 'staff'
            return redirect(url_for("auth.staff_dashboard", name=usr.username, id=usr.id))
        else:
            flash('Invalid user credentials', 'denger')
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
        usr=Users.query.filter_by(email=email).first()
        if usr:
            flash('Sorry, this mail already registered', 'danger')
            return render_template("register.html",msg="Sorry, this mail already registered!!!")
        new_usr=Users(username=uname,email=email,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        flash('Registration successful! Login to get Started', 'success')
        return redirect(url_for('auth.login'))
    return render_template("register.html",msg="")


@auth_bp.route("/admin_dashboard")
def admin_dashboard():
    
    return render_template("admin_dashboard.html")

@auth_bp.route("/user_dashboard")
def user_dashboard():
    
    return render_template("user_dashboard.html")

@auth_bp.route("/staff_dashboard")
def staff_dashboard():
    
    return render_template("staff_dashboard.html")



@auth_bp.route("/register_staff", methods=["GET", "POST"])
def register_staff():
    if request.method == "POST":
        uname = request.form.get("username")
        pwd = request.form.get("password")
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        experience_years= request.form.get("experience_years")
        specialization = request.form.get("specialization")
        user_id = request.form.get("user_id")
        joined_at_str = request.form.get("joined_at")
        joined_at = datetime.strptime(joined_at_str, "%Y-%m-%d").date()


        # Check duplicate
        usr = Users.query.filter_by(username=uname).first()
        if usr:
            flash('Sorry, this Username is alredy taken!', 'danger')
            return render_template("register_staff.html", msg="Username already taken!")

        # Create Users entry
        new_staff = Users(
            username=uname,
            email=email,
            password=pwd,
            full_name=full_name,
            address="N/A",       # not needed for staff
            pin_code="N/A",   # placeholder
            role=2,
            is_approved=False
        )
        db.session.add(new_staff)
        db.session.flush()  # get new_staff.id before commit

        # Create Staff_profile entry simultaneously
        staff_profile = Staff_profile(
            name=full_name,
            user_id=new_staff.id,
            phone=phone,
            experience_years=experience_years,
            joined_at=joined_at,
            specialization=specialization
            
        )
        db.session.add(staff_profile)
        db.session.commit()

        return redirect(url_for('auth.login'))
    return render_template("register_staff.html", msg="")

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    #return redirect(url_for('auth.login'))
    return render_template('login.html')


@auth_bp.route('/admin_dashboard/staff')
def staff():
    active_tab = request.args.get('tab', 'pending')

    pending_staff = db.session.query(Users, Staff_profile).join(
        Staff_profile, Staff_profile.user_id == Users.id
    ).filter(Users.role == 2, Users.is_approved == False).all()

    approved_staff = db.session.query(Users, Staff_profile).join(
        Staff_profile, Staff_profile.user_id == Users.id
    ).filter(Users.role == 2, Users.is_approved == True).all()

    return render_template('approve_staff.html',pending_staff=pending_staff,approved_staff=approved_staff,active_tab=active_tab)


@auth_bp.route('/admin_dashboard/')
def dashboard():
    return render_template('admin_dashboard.html')


@auth_bp.route('/admin_dashboard/approve/<int:user_id>')
def approve_staff(user_id):
    usr = Users.query.get(user_id)
    if usr and usr.role == 2:
        usr.is_approved = True
        db.session.commit()
    return redirect(url_for('auth.staff', tab='pending'))


@auth_bp.route('/admin_dashboard/reject/<int:user_id>')
def reject_staff(user_id):
    usr = Users.query.get(user_id)
    if usr and usr.role == 2:
        Staff_profile.query.filter_by(user_id=user_id).delete()
        db.session.delete(usr)
        db.session.commit()
    return redirect(url_for('auth.staff', tab='pending'))





