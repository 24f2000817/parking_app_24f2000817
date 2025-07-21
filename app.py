from flask import Flask, render_template
from controllers.database import *
from controllers.config import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

with app.app_context():
    db.create_all() # Create tables if they don't exist

    Admin = User.query.filter_by(email = 'admin@gmail.com').first()
    if not Admin:
        Admin = User(
            username='admin',
            email='admin@gmail.com',
            password='admin@123',
            phone_number='1234567890'
        )
        db.session.add(Admin)
    db.session.commit()

@app.route("/")
def home():
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    search = request.args.get('search', None)
    search_type = request.args.get('search_type',None)
    if search_type == 'location':
        search_results = ParkingLot.query.filter_by( address = search ).all()
    elif search_type == 'pincode':
        search_results = ParkingLot.query.filter_by( pin_code = search ).all()
    else:
        search_results = ParkingLot.query.all()
    reservations = Reservation.query.all()
        
    return render_template("home.html", lots = lots, spots = spots, search_results=search_results, reservations=reservations)

from controllers.authentication import *
from controllers.routes import *

if __name__ == "__main__":
    app.run(debug=True)