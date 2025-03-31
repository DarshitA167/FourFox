from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for ,  jsonify
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/USER'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class USERS(UserMixin, db.Model):  # Inherit from UserMixin
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), unique=False, nullable=False)
    Phone = db.Column(db.String(12), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(20), unique=False, nullable=False)

    # Flask-Login requires this method to get the user ID
    def get_id(self):
        return str(self.ID)


# Serve model files
@app.route('/static/my_model/<path:filename>')
def serve_model(filename):
    return send_from_directory('static/my_model', filename)


#basic

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@login_manager.user_loader
def load_user(user_id):
    return USERS.query.get(int(user_id))

# Your existing login function (unchanged)
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('logged_in.html', email=current_user.Email, password=current_user.Password)  

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = USERS.query.filter((USERS.Email == email) & (USERS.Password == password)).first()
        existing_user1 = USERS.query.filter((USERS.Email == email) & (USERS.Password != password)).first()

        if existing_user:
            login_user(existing_user)  # Save login session
            return redirect(url_for('index'))  # Redirect to index
        
        if existing_user1:
            flash("Incorrect Password or Email. Please try again.", "danger")
            return redirect(url_for('login'))
        
        flash("No User With These Credentials Found. Try Registering instead", "danger")
        return redirect(url_for('register'))

    return render_template('login.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email or phone already exists
        existing_user = USERS.query.filter((USERS.Email == email) | (USERS.Phone == phone)).first()

        if existing_user:
            flash("Email or Phone Number already registered. Please use a different one.", "danger")
            return redirect(url_for('register'))  # Redirect back to registration page
        
        # If no existing user, add to the database
        entry = USERS(Name=name, Phone=phone, Email=email, Password=password)
        db.session.add(entry)
        db.session.commit()

        return redirect(url_for('index'))  # Redirect to index after successful registration
        flash("Registration successful! You can now log in.", "success")
        
    return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True, port=5004)


