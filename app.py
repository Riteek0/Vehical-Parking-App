from flask import Flask, render_template, redirect, url_for, request, session, flash
from model import db, init_db,User, ParkingLot, ParkingSpot, Reservation, SpotStatus
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from model import create_admin_if_not_exists 
import os # <-- Import the OS library

app = Flask(__name__)

# --- DATABASE AND SECRET KEY CONFIG ---
# This is the new, important part.
# It checks if we are on a live server (Render) or your local computer.

# Get the cloud database URL from the "environment variables" (which Render will provide)
db_url = os.environ.get('DATABASE_URL')

if db_url:
    # We are on the live server (Render)
    # The 'postgres' protocol needs to be changed to 'postgresql' for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://", 1)
else:
    # We are on your local computer
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'

# Get the SECRET_KEY from environment variables.
# We will set this on Render.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_local_secret_key')
# --- END OF NEW CONFIG ---


# Initialize the database with our app
init_db(app)

# Create database tables (and the admin user) if they don't exist
# This will run both locally and on the live server
with app.app_context():
    db.create_all()
    create_admin_if_not_exists()


@app.route('/')
def home():
    return render_template('home.html')

#--- User Registration 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        full_name = request.form['full_name']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=username, password=password, email=email, full_name=full_name, role='user')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

# --- User Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

# --- Admin Dashboard 
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # --- New Summary Calculations ---
    lots = ParkingLot.query.all()
    users = User.query.filter(User.role != 'admin').all()
    
    total_lots = len(lots)
    total_users = len(users)
    occupied_spots = ParkingSpot.query.filter_by(status=SpotStatus.OCCUPIED).count()
    total_spots = ParkingSpot.query.count()
    available_spots = total_spots - occupied_spots
    # --- End of Summary Calculations ---

    return render_template(
        'admin_dashboard.html', 
        lots=lots, 
        users=users,
        total_lots=total_lots,
        total_users=total_users,
        occupied_spots=occupied_spots,
        available_spots=available_spots
    )

# ---- Admin view for Parking Lot Details
@app.route('/admin/lot_details/<int:lot_id>')
def admin_lot_details(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    active_reservations = db.session.query(Reservation).join(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id,
        Reservation.leaving_timestamp == None
    ).all()
    reservation_map = {res.spot_id: res for res in active_reservations}
    return render_template('admin_lot_details.html', lot=lot, reservation_map=reservation_map)

# --- Creating Parking Lot 
@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_lot():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['prime_location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['maximum_number_of_spots'])
        lot = ParkingLot(prime_location_name=name, price=price, address=address, pin_code=pin_code, maximum_number_of_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        # Create parking spots
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE)
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot created successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_lot.html')

# --- Edit Parking Lot 
@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        new_max_spots = int(request.form['maximum_number_of_spots'])
        current_spots = len(lot.spots)
        if new_max_spots > current_spots:
            for _ in range(new_max_spots - current_spots):
                spot = ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE)
                db.session.add(spot)
        elif new_max_spots < current_spots:
            removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status=SpotStatus.AVAILABLE).limit(current_spots - new_max_spots).all()
            for spot in removable_spots:
                db.session.delete(spot)
        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_lot.html', lot=lot)

# --- Delete Parking Lot 
@app.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    # --- TYPO FIX: Changed spot..status to spot.status ---
    if all(spot.status == SpotStatus.AVAILABLE for spot in lot.spots):
        db.session.delete(lot)
        db.session.commit()
        flash('Parking lot deleted!')
    else:
        flash('Cannot delete lot with occupied spots.')
    return redirect(url_for('admin_dashboard'))

# --- User Dashboard 
@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    lots = ParkingLot.query.all()
    user = User.query.get(session['user_id'])
    reservations = user.reservations
    return render_template('user_dashboard.html', lots=lots, reservations=reservations,user=user)

# --- Reserve Parking Spot
@app.route('/reserve/<int:lot_id>', methods=['POST'])
def reserve_spot(lot_id):
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status=SpotStatus.AVAILABLE).first()
    if not spot:
        flash('No available spots in this lot.')
        return redirect(url_for('user_dashboard'))
    spot.status = SpotStatus.OCCUPIED
    vehicle_number = request.form.get('vehicle_number', 'N/A')
    reservation = Reservation(
        spot_id=spot.id,
        user_id=session['user_id'],
        parking_timestamp=datetime.utcnow(),
        parking_cost=lot.price,
        vehicle_number=vehicle_number
    )
    db.session.add(reservation)
    db.session.commit()
    flash('Spot reserved successfully!')
    return redirect(url_for('user_dashboard'))

# --- Release Parking Spot 
@app.route('/release/<int:reservation_id>', methods=['POST'])
def release_spot(reservation_id):
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        flash('Unauthorized action.')
        return redirect(url_for('user_dashboard'))
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = SpotStatus.AVAILABLE
    reservation.leaving_timestamp = datetime.utcnow()
    db.session.commit()
    flash('Spot released!')
    return redirect(url_for('user_dashboard'))

# --- Logout 
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
