from flask import redirect, render_template, session, request, flash
from flask_app import app
from flask_app.models import user


@app.route('/register', methods=['POST'])
def register():
    try:
        if session['current_id']:
            return redirect('/')
    except KeyError:
        if not user.User.validate_reg(request.form):
            return redirect('/register_page')

        pw_hash = user.bcrypt.generate_password_hash(request.form['password'])

        data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'password': pw_hash
        }

        current_user = user.User.add_user(data)
        session['current_id'] = current_user
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    try:
        if session['current_id']:
            return redirect('/')
    except KeyError:
        if not user.User.validate_login(request.form):
            return redirect('/login_page')

        data = {'username': request.form['username']}
        current_user = user.User.get_user_by_username(data)

        session['current_id'] = current_user.id
        return redirect('/')


@app.route('/register_page')
def render_register_page():
    try:
        if session['current_id']:
            return redirect('/')
    except KeyError:
        return render_template('register.html')


@app.route('/login_page')
def render_login_page():
    try:
        if session['current_id']:
            return redirect('/')
    except KeyError:
        return render_template('login.html')
