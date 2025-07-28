from app import app
from flask import render_template, redirect, url_for, request, flash, session
from controllers.database import *
import pytz

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
                prime_location_name = request.form.get("locationName")
                address = request.form.get("address")
                pin_code = request.form.get("pincode")
                price = float(request.form.get("price"))
                maximum_number_of_spots = int(request.form.get("maximumSpots"))

                if maximum_number_of_spots > lot.maximum_number_of_spots:
                    for _ in range(maximum_number_of_spots - lot.maximum_number_of_spots):
                        new_spot = ParkingSpot(lot_id=lot.id, status='A')
                        db.session.add(new_spot)
                
                elif maximum_number_of_spots < ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count():
                    flash("Cannot reduce the number of spots. There are currently reserved parking spots.", "error")
                    return redirect(url_for("edit_lot", lot_id=lot.id))
                
                elif maximum_number_of_spots < lot.maximum_number_of_spots:
                    for _ in range(lot.maximum_number_of_spots - maximum_number_of_spots):
                        delete_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').order_by(ParkingSpot.id.desc()).first()
                        db.session.delete(delete_spot)
                
                if not prime_location_name:
                    flash("Location name is required.", "error")
                    return render_template("edit_lot.html", lot=lot)
                
                if not address:
                    flash("Address is required.", "error")
                    return render_template("edit_lot.html", lot=lot)
                
                if not pin_code:
                    flash("Pin code is required.", "error")
                    return render_template("edit_lot.html", lot=lot)
                
                if not price:
                    flash("Price is required.", "error")
                    return render_template("edit_lot.html", lot=lot)
                
                if not maximum_number_of_spots:
                    flash("Maximum number of spots is required.", "error")
                    return render_template("edit_lot.html", lot=lot)

                lot.prime_location_name = prime_location_name
                lot.address = address
                lot.pin_code = pin_code
                lot.price = price
                lot.maximum_number_of_spots = maximum_number_of_spots

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

        if spot.status == 'O':
            flash("Cannot delete a reserved parking spot.", "error")
            return redirect(url_for("home"))
        if spot:
            spot.lot.maximum_number_of_spots -= 1
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
    ist = pytz.timezone('Asia/Kolkata')
    if session.get("user_email") == 'admin@gmail.com':
        spot = ParkingSpot.query.get(spot_id)
        if spot:
            current_timestamp = datetime.now(ist)
            reservation = Reservation.query.filter_by(spot_id=spot_id).first()
            estimated_cost = round((current_timestamp - ist.localize(reservation.parking_timestamp)).total_seconds() / 3600 * reservation.cost_per_hour,2)
            return render_template("view_spot_details.html", spot=spot, current_timestamp=current_timestamp, estimated_cost=estimated_cost)
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

@app.route("/booking/<int:lot_id> ", methods=["GET", "POST"])
def booking(lot_id):
    ist = pytz.timezone('Asia/Kolkata')
    if 'user_email' in session:
        if request.method == "GET":
            lot = ParkingLot.query.get(lot_id)
            spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
            user_id = session.get("user_id")
            return render_template("booking.html", lot=lot, spot=spot, user_id=user_id)
        if request.method == "POST":
            spot_id = request.form.get("spot_id")
            vehicle_number = request.form.get("vehicle_number")
            user_id = session.get("user_id")
            lot = ParkingLot.query.get(lot_id)

            if not spot_id or not vehicle_number:
                flash("Spot ID and Vehicle Number are required.", "error")
                return redirect(url_for("booking", lot_id=lot_id))

            spot = ParkingSpot.query.get(spot_id)
            if not spot or spot.status != 'A':
                flash("Selected parking spot is not available.", "error")
                return redirect(url_for("booking", lot_id=lot_id))

            new_reservation = Reservation(
                spot_id=spot.id,
                user_id=user_id,
                vehicle_number=vehicle_number,
                parking_timestamp=datetime.now(ist),
                cost_per_hour= lot.price
            )
            spot.status = 'O'
            db.session.add(new_reservation)
            db.session.commit()
            flash("Booking successful!", "success")
            return redirect(url_for("home"))
    else:
        flash("You need to log in to book a parking spot.", "error")
        return redirect(url_for("login"))
    
@app.route("/release/<int:spot_id>", methods=["GET", "POST"])
def release(spot_id):
    ist = pytz.timezone('Asia/Kolkata')
    if 'user_email' in session:
        spot = ParkingSpot.query.get(spot_id)
        reservation = Reservation.query.filter_by(spot_id=spot_id, leaving_timestamp=None).first()
        current_timestamp = datetime.now(ist)
        if request.method == "GET":
            if reservation:
                duration = (current_timestamp - ist.localize(reservation.parking_timestamp)).total_seconds() / 3600
                total_cost = round(duration * reservation.cost_per_hour,2)
                return render_template("release.html", spot=spot, reservation=reservation, total_cost=total_cost, current_timestamp=current_timestamp, duration=duration)
            else:
                flash("No active reservation found for this spot.", "error")
                return redirect(url_for("home"))
        if request.method == "POST":
            if reservation:
                reservation.leaving_timestamp = current_timestamp
                spot.status = 'A'
                db.session.commit()
                flash("Spot released successfully!", "success")
                return redirect(url_for("home"))
            else:
                flash("No active reservation found for this spot.", "error")
                return redirect(url_for("home"))
    else:
        flash("You need to log in to release a parking spot.", "error")
        return redirect(url_for("login"))
    
@app.route("/records")
def records():
    if session.get("user_email") == 'admin@gmail.com':
        reservations = Reservation.query.all()
        return render_template("records.html", reservations=reservations)
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))
    
@app.route("/adminsearch", methods=["GET", "POST"])
def adminsearch():
    if session.get("user_email") == 'admin@gmail.com':
        search = request.args.get('search', None)
        search_type = request.args.get('search_type',None)
        if search_type == 'username':
            results = User.query.filter_by( username = search ).all()
        if search_type == 'spot_id':
            results = ParkingSpot.query.filter_by( id = search ).all()
        return render_template("adminsearch.html", results=results, search_type=search_type)
    else:
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for("home"))