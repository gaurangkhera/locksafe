from hack import app, create_db, db
from flask import render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm
from hack.models import User, Locker
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

stripe.api_key = app.config['STRIPE_SECRET_KEY']

create_db(app)


# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')


# AJAX route for Stripe payments
@app.route('/stripe_pay/<locker_id>')
def stripe_pay(locker_id):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NTgYsSAvDl2UTdKUmRdLnFD',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True, locker_id=locker_id) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('home', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/thanks/<locker_id>')
def thanks(locker_id):
    locker = Locker.query.filter_by(id=locker_id).first()
    locker.lock_locker(current_user.id)
    return render_template('thanks.html', locker=locker)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists'
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
    return render_template('reg.html', form=form, mess=mess)

@app.route('/lockers')
def show_lockers():
    lockers = Locker.query.all()
    return render_template('lockers.html', lockers=lockers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password.'
    return render_template('login.html', mess=mess, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
