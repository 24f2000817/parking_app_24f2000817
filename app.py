from flask import Flask
from controllers.database import db, User, ParkingLot, ParkingSpot, Reservation
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
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)