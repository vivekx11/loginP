from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_DIR = 'user_data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_file(username):
    return os.path.join(DATA_DIR, f"{username}.json")

def load_user_data(username):
    filepath = get_user_file(username)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(username, data):
    filepath = get_user_file(username)
    with open(filepath, 'w') as f:
        json.dump(data, f)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username and password:
            user_data = load_user_data(username)
            if user_data.get('password') == password:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not username or not password:
            return render_template('signup.html', error='All fields are required')
        if os.path.exists(get_user_file(username)):
            return render_template('signup.html', error='User already exists')
        save_user_data(username, {"password": password})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    data = load_user_data(username)
    return render_template('dashboard.html', username=username, user_data=json.dumps(data))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/save', methods=['POST'])
def save():
    if 'username' not in session:
        return "Unauthorized", 401
    data = request.json
    username = session['username']
    user_data = load_user_data(username)
    user_data.update(data)
    save_user_data(username, user_data)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
