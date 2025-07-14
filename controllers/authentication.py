from app import app
from flask import render_template, redirect, url_for, request, flash, session
from controllers.database import *

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_email' in session:
            flash("You are already logged in.", "info")
            return redirect(url_for("home"))
        return render_template("login.html")
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Email is required.", "error")
            return render_template("login.html")
        
        if not password:
            flash("Password is required.", "error")
            return render_template("login.html")
        
        if '@' not in email:
            flash("Invalid email format.", "error")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        
        if user.password != password:
            flash("Incorrect password.", "danger")
            return render_template("login.html")
        
        session["user_email"] = user.email
        session["user_id"] = user.id
        flash("Login successful!", "success")
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    if 'user_email' not in session:
        flash("You are not logged in.", "info")
        return redirect(url_for("login"))
    
    session.pop("user_email", None)
    session.pop("user_id", None)
    flash("Logout successful!", "success")
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if 'user_email' in session:
            flash("You have already logged in.", "info")
            return redirect(url_for("home"))
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        phone_number = request.form.get("phone_number")

        if not username:
            flash("Username is required.", "error")
            return render_template("register.html")
        
        if not email:
            flash("Email is required.", "error")
            return render_template("register.html")
        
        if '@' not in email:
            flash("Invalid email format.", "error")
            return render_template("register.html")
        
        if not password:
            flash("Password is required.", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        
        if not phone_number:
            flash("Phone number is required.", "error")
            return render_template("register.html")
        
        if len(phone_number) < 8 or len(phone_number) > 20:
            flash("Phone number must be between 8 and 20 characters.", "error")
            return render_template("register.html")
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", "error")
            return render_template("login.html")
        
        new_user = User(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))
    
    