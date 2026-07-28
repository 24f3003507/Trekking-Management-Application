#App routes
from flask import Blueprint, Flask, app,render_template,request,url_for,redirect,flash ,session 
from backend.models import *
from datetime import datetime
from datetime import date
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
            session['id'] = usr.id 
            return redirect(url_for("auth.user_dashboard",name=uname,id=usr.id))
        
        elif usr and usr.role == 2:  # Staff
            if not usr.is_approved:
                return render_template("login.html", msg="Your account is pending admin approval.")
            session.clear()
            session['username'] = usr.username
            session['role'] = 'staff'
            session['id'] = usr.id
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
    total_treks = Trek.query.count()
    total_users = Users.query.count()
    total_staff = Staff_profile.query.count()
    total_bookings = Booking.query.count()
    bookings = db.session.query(Booking, Trek, Users).join(Trek, Booking.trek_id == Trek.id).join(Users, Booking.user_id == Users.id).all()
    return render_template("admin_dashboard.html",bookings=bookings , total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings)

@auth_bp.route('/user_dashboard')
def user_dashboard():
    user_id = request.args.get('id')
    treks = Trek.query.all()      # Add new Trek (save clik) data will show in user_dashboard also due to this
    bookings = db.session.query(Booking, Trek).join(Trek, Booking.trek_id == Trek.id).filter(Booking.user_id == user_id).all()

#I used a join here because my Booking model doesn't store trek_name directly — i need to join with Trek to display it.

    return render_template('user_dashboard.html', treks=treks, bookings=bookings)

@auth_bp.route("/staff_dashboard")
def staff_dashboard():
    
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    staff = Staff_profile.query.filter_by(user_id=user_id).first()
    if not staff:
        flash("Staff profile not found", "danger")
        return redirect(url_for('auth_bp.login'))

    # Only treks assigned to this staff member
    treks = Trek.query.filter_by(assigned_staff_id=staff.id).all()

    trek_data = []
    total_participants = 0
    open_treks_count = 0

    for trek in treks:
        # count bookings for this trek, excluding cancelled ones
        participant_count = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.booking_status != "Cancelled"
        ).count()

        total_participants += participant_count
        if trek.status not in ("Completed", "Inactive"):
            open_treks_count += 1
        trek_data.append({
            'id': trek.id,
            'name': trek.trek_name,
            'location': trek.location,
            'participants': participant_count,
            'slots': trek.available_slots,
            'status': trek.status
        })

    return render_template(
        "staff_dashboard.html",
        treks=trek_data,
        assigned_treks=len(treks),
        participants=total_participants,
        open_treks=open_treks_count
    )

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

    total_treks = Trek.query.count()
    total_users = Users.query.count()
    total_staff = Staff_profile.query.count()
    total_bookings = Booking.query.count()

    active_tab = request.args.get('tab', 'pending')

    pending_staff = db.session.query(Users, Staff_profile).join(
        Staff_profile, Staff_profile.user_id == Users.id
    ).filter(Users.role == 2, Users.is_approved == False).all()

    approved_staff = db.session.query(Users, Staff_profile).join(
        Staff_profile, Staff_profile.user_id == Users.id
    ).filter(Users.role == 2, Users.is_approved == True).all()

    return render_template('approve_staff.html',pending_staff=pending_staff,approved_staff=approved_staff,active_tab=active_tab,
                           total_treks=total_treks,total_users=total_users,total_staff=total_staff,total_bookings=total_bookings)


@auth_bp.route('/admin_dashboard/')
def dashboard():
    role = session.get('role')

    if role == 'admin':
        return redirect(url_for('auth.admin_dashboard'))
    elif role == 'user':
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=session.get('id')))
    elif role == 'staff':
        return redirect(url_for('auth.staff_dashboard', name=session.get('username'), id=session.get('id')))
    else:
        return redirect(url_for('auth.login'))



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

@auth_bp.route('/admin_dashboard/blacklist/<int:user_id>')
def blacklist_staff(user_id):
    usr = Users.query.get(user_id)
    if usr and usr.role == 2:
        usr.is_approved = False  # just flip back to False
        db.session.commit()
    return redirect(url_for('auth.staff', tab='approved'))


@auth_bp.route('/admin_dashboard/reactivate/<int:user_id>')
def reactivate_staff(user_id):
    usr = Users.query.get(user_id)
    if usr and usr.role == 2:
        usr.is_approved = True
        db.session.commit()
    return redirect(url_for('auth.staff', tab='pending'))


@auth_bp.route('/admin_dashboard/trek')
def trek():

    total_treks = Trek.query.count()
    total_users = Users.query.count()
    total_staff = Staff_profile.query.count()
    total_bookings = Booking.query.count()

    treks = Trek.query.all()
    return render_template('admin_trek.html', treks=treks, total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings)

@auth_bp.route('/admin_dashboard/trek/add_trek', methods=['GET', 'POST'])
def add_trek():
    if request.method == 'POST':
        trek_name = request.form.get('trek_name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        available_slots = request.form.get('available_slots')
        assigned_staff = request.form.get('assigned_staff')
        status = request.form.get('status')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        new_trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration_days=int(duration),
            available_slots=int(available_slots),
            assigned_staff_id=int(assigned_staff) if assigned_staff else None,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('auth.trek'))
    
#Admin assign approved staff to Trek here

    approved_staff = db.session.query(Staff_profile).join(
        Users, Staff_profile.user_id == Users.id
    ).filter(Users.role == 2, Users.is_approved == True).all()
    return render_template('/add_trek.html', staff_list=approved_staff)


@auth_bp.route('/admin_dashboard/trek/delete/<int:trek_id>')
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if trek:
        db.session.delete(trek)
        db.session.commit()
    return redirect(url_for('auth.trek'))



@auth_bp.route('/admin_dashboard/users/delete/<int:user_id>')
def delete_user(user_id):
    user = Users.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('auth.users_data'))
    


@auth_bp.route('/book_trek/<int:trek_id>')
def book_trek(trek_id):
    if session.get('role') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('id') 

    # Prevent duplicate booking
    existing_booking = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek_id
    ).filter(Booking.booking_status != 'Cancelled').first()

    if existing_booking:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))


    trek = Trek.query.get(trek_id)
    if not trek:
        flash('Trek not found', 'danger')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))

    if trek.status.lower() == 'inactive':
        flash('This trek is currently inactive and not accepting bookings.', 'warning')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))

    if trek.available_slots <= 0:
        flash('Trek not available', 'danger')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))

    new_booking = Booking(
        booking_status='Pending',
        booking_date=datetime.now().date(),
        payment_status='Pending',
        user_id=user_id,
        trek_id=trek_id
    )
    db.session.add(new_booking)

    trek.available_slots -= 1  # reduce slot count
    db.session.commit()

    flash('Trek booked successfully!', 'success')
    return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))



@auth_bp.route('/admin_dashboard/trekking_history')
def trekking_history():
    bookings = db.session.query(Booking, Trek, Users).join(Trek, Booking.trek_id == Trek.id).join(Users, Booking.user_id == Users.id).all()
    return render_template('trekking_history.html', bookings=bookings)
    

@auth_bp.route('/admin_dashboard/users')
def users_data():
    users = Users.query.all()
    
    return render_template('users_data.html', users=users)


@auth_bp.route('/user_dashboard/browse_treks')
def browse_treks():
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')

    query = Trek.query
    if search:
        query = query.filter(Trek.trek_name.ilike(f'%{search}%'))
    if difficulty:
        query = query.filter(Trek.difficulty.ilike(f'%{difficulty}%'))
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    treks = query.all()
    return render_template('browse_treks.html', treks=treks)


@auth_bp.route('/user_dashboard/browse_treks/<int:trek_id>')
def trek_details(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        flash('Trek not found', 'danger')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=session.get('id')))

    slug = trek.trek_name.strip().lower().replace(' ', '_') + '.html'
    return render_template([slug, 'trek_details_generic.html'], trek=trek)


@auth_bp.route('/user_dashboard/booking_history')
def booking_history():
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth.login'))

    bookings = (
        db.session.query(Booking)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(
            Booking.user_id == user_id,
            Trek.status.ilike('completed')
        )
        .all()
    )

    return render_template('booking_history.html', bookings=bookings)


@auth_bp.route('/user_dashboard/profile', methods=['GET', 'POST'])
def update_profile():
    user_id = session.get('id')
    user = Users.query.get(user_id)

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))

    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.phone_number = request.form.get('phone_number')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.user_dashboard', name=session.get('username'), id=user_id))

    return render_template('update_profile.html', user=user)


@auth_bp.route('/admin_dashboard/search')
def admin_search():
    query = request.args.get('q', '').strip()
    treks, staff, users = [], [], []

    if query:
        treks = Trek.query.filter(
            db.or_(
                Trek.trek_name.ilike(f"%{query}%"),
                Trek.location.ilike(f"%{query}%"),
                db.cast(Trek.id, db.String) == query
            )
        ).all()

        staff = Staff_profile.query.filter(
            db.or_(
                Staff_profile.name.ilike(f"%{query}%"),
                db.cast(Staff_profile.id, db.String) == query
            )
        ).all()

        users = Users.query.filter(
            db.or_(
                Users.full_name.ilike(f"%{query}%"),
                Users.username.ilike(f"%{query}%"),
                db.cast(Users.id, db.String) == query
            )
        ).all()

    return render_template(
        'search.html',
        query=query,
        treks=treks,
        staff=staff,
        users=users
    )


@auth_bp.route('/staff_dashboard/manage_trek/<int:trek_id>')
def manage_trek(trek_id):
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    staff = Staff_profile.query.filter_by(user_id=user_id).first()
    if not staff:
        flash("Staff profile not found", "danger")
        return redirect(url_for('auth_bp.login'))

    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter(
        Booking.trek_id == trek.id,
        Booking.booking_status != "Cancelled"
    ).all()

    return render_template('manage_trek.html', trek=trek, bookings=bookings, name=session.get('name'))


@auth_bp.route('/staff_dashboard/view_trek/<int:trek_id>')
def view_trek(trek_id):
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    staff = Staff_profile.query.filter_by(user_id=user_id).first()
    if not staff:
        flash("Staff profile not found", "danger")
        return redirect(url_for('auth_bp.login'))

    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter(
        Booking.trek_id == trek.id,
        Booking.booking_status != "Cancelled"
    ).all()

    return render_template('view_trek.html', trek=trek, bookings=bookings, name=session.get('name'))


@auth_bp.route('/staff_dashboard/manage_trek/<int:trek_id>/update', methods=['POST'])
def update_trek(trek_id):
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth.login'))

    staff = Staff_profile.query.filter_by(user_id=user_id).first()
    if not staff:
        flash("Staff profile not found", "danger")
        return redirect(url_for('auth.login'))

    trek = Trek.query.get_or_404(trek_id)

    trek.available_slots = int(request.form.get('available_slots', trek.available_slots))
    trek.status = request.form.get('status', trek.status)

    db.session.commit()
    flash("Trek updated successfully", "success")
    return redirect(url_for('auth.manage_trek', trek_id=trek.id))

@auth_bp.route("/staff_dashboard/participants")
def staff_participants():
    user_id = session.get('id')
    if not user_id:
        flash("Please login first", "danger")
        return redirect(url_for('auth.login'))

    staff = Staff_profile.query.filter_by(user_id=user_id).first()
    if not staff:
        flash("Staff profile not found", "danger")
        return redirect(url_for('auth.login'))

    treks = Trek.query.filter_by(assigned_staff_id=staff.id).all()
    trek_ids = [t.id for t in treks]

    bookings = Booking.query.filter(
        Booking.trek_id.in_(trek_ids),
        Booking.booking_status != "Cancelled"
    ).all()

    return render_template(
        'staff_participants.html',
        bookings=bookings,
        name=session.get('name')
    )