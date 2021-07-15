from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, send_file
from .models import Codes, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import webbrowser
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                print(user.id)
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Invalid Password', category='error')
        else:
            flash('Invalid Email', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        if request.form['submit_button'] == 'a':
            code = request.form.get('code')
            if code != '':
                ccode = Codes.query.filter_by(code=code).first()
                if not ccode:
                    flash('Invalid discount Code', category='error')
                    flash('Try Code "Halve" for a 50% Disscount ;)', category='error')
                else:
                    webbrowser.open_new_tab(str(ccode.link))
            else:
                webbrowser.open_new_tab(str('ccode.link'))
        elif request.form['submit_button'] == 'b':
            code = request.form.get('code')
            code = code.split(',')
            print(code)
            new_code = Codes(code= code[0], link= code[1])
            db.session.add(new_code)
            db.session.commit()
            print(f'[success]: {code[0]} added.')

    return render_template('checkout.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route("/static")
def static_dir(path):
    return send_from_directory("static", path)

@auth.route('/downloads')
def donloads():
    return render_template('downloads.html', user=current_user)

@auth.route('/doit/<cual>')
def download_file(cual):
    a = f'./static/downloads/{cual}'
    return send_file(a, as_attachment=True)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        userName = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        if 100 < len(email) < 4:
            flash('Email must be grater than 4 characters.', category='error')
        elif 25 < len(userName) < 4:
            if len(userName) <4:
                flash('Username must be grater than 3 characters.', category='error')
            else: 
                flash('Username must be shorter than 25 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif 50 < len(password1) < 7:
            if len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                flash('Password is TOO long', category='error')
        else:
            new_user = User(email=email, userName=userName, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created succesfully!.', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)