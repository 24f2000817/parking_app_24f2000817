from app import app
from flask import render_template, redirect, url_for, request, flash, session
from controllers.database import *

@app.route("/addlot", methods=["GET", "POST"])
def add_lot():
    if session.get("user_email") == 'admin@gmail.com':
        if request.method == "GET":
            return render_template("addlot.html")
        
        if request.method == "POST":
            prime_location_name = request.form.get("locationName")
            address = request.form.get("address")
            pin_code = request.form.get("pincode")
            price = float(request.form.get("price"))
            maximum_number_of_spots = int(request.form.get("maximumSpots"))

            if not prime_location_name:
                flash("Location name is required.", "error")
                return render_template("addlot.html")
            
            if not address:
                flash("Address is required.", "error")
                return render_template("addlot.html")
            
            if not pin_code:
                flash("Pin code is required.", "error")
                return render_template("addlot.html")
            
            if not price:
                flash("Price is required.", "error")
                return render_template("addlot.html")
            
            if not maximum_number_of_spots:
                flash("Maximum number of spots is required.", "error")
                return render_template("addlot.html")
            
            if not pin_code.isdigit() or len(pin_code) != 6:
                flash("Pin code must be a 6-digit number.", "error")
                return render_template("addlot.html")
            
            new_lot = ParkingLot(
                prime_location_name=prime_location_name,
                address=address, 
                pin_code=pin_code, 
                price=price, 
                maximum_number_of_spots=maximum_number_of_spots
            )
            
            db.session.add(new_lot)
            db.session.commit()

            for _ in range(maximum_number_of_spots):
                new_spot = ParkingSpot(lot_id=new_lot.id, status='A')
                db.session.add(new_spot)
            db.session.commit()

            flash("Parking lot added successfully!", "success")
            return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")    
        return redirect(url_for("home"))
    
@app.route("/delete_lot/<int:lot_id>")
def delete_lot(lot_id):
    if session.get("user_email") == 'admin@gmail.com':
        lot = ParkingLot.query.get(lot_id)
        if lot:
            db.session.delete(lot)
            db.session.commit()
            flash("Parking lot deleted successfully!", "success")
        else:
            flash("Parking lot not found.", "error")
        return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))
    
@app.route("/edit_lot/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    if session.get("user_email") == 'admin@gmail.com':
        lot = ParkingLot.query.get(lot_id)
        if lot:
            if request.method == "GET":
                return render_template("edit_lot.html", lot=lot)
            if request.method == "POST":
                lot.prime_location_name = request.form.get("locationName")
                lot.address = request.form.get("address")
                lot.pin_code = request.form.get("pincode")
                lot.price = float(request.form.get("price"))
                lot.maximum_number_of_spots = int(request.form.get("maximumSpots"))
                db.session.commit()
                flash("Parking lot edited successfully!", "success")
                return redirect(url_for("home"))
        else:
            flash("Parking lot not found.", "error")
            return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))
    
@app.route("/delete_spot/<int:spot_id>")
def delete_spot(spot_id):
    if session.get("user_email") == 'admin@gmail.com':
        spot = ParkingSpot.query.get(spot_id)
        if spot:
            db.session.delete(spot)
            db.session.commit()
            flash("Parking spot deleted successfully!", "success")
        else:
            flash("Parking spot not found.", "error")
        return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))

@app.route("/view_spot/<int:spot_id>")
def view_spot(spot_id):
    if session.get("user_email") == 'admin@gmail.com':
        spot = ParkingSpot.query.get(spot_id)
        if spot:
            return render_template("view_spot.html", spot=spot)
        else:
            flash("Parking spot not found.", "error")
            return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))
    
@app.route("/view_spot_details/<int:spot_id>")
def view_spot_details(spot_id):
    if session.get("user_email") == 'admin@gmail.com':
        spot = ParkingSpot.query.get(spot_id)
        if spot:
            return render_template("view_spot_details.html", spot=spot)
        else:
            flash("Parking spot not found.", "error")
            return redirect(url_for("home"))
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))
    
@app.route("/users")
def users():
    if session.get("user_email") == 'admin@gmail.com':
        users = User.query.all()
        usersdata = []
        for user in users:
            frequency = Reservation.query.filter_by(user_id=user.id).count() or 0
            usersdata.append((user, frequency))
        return render_template("users.html", userdata=usersdata)
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))