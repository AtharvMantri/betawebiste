import random
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/helpapp'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'betawebsiteproject@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'nualhajvlaznvqzd'  # Update with your email password
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Helper(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)    
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(100), nullable=False)

class HelpRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('requests', lazy=True))
    task = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(2000), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    helper_id = db.Column(db.Integer, db.ForeignKey('helper.id'))
    helper = db.relationship('Helper', backref=db.backref('requests', lazy=True))

# definations
def send_approval_email(user_email, time, date, work, name, id):
    msg = Message('Request Approved', sender='betawebsiteproject@gmail.com', recipients=[user_email])
    msg.body = f'''Dear User,

Your request for the work of {work} has been approved by our helper {name}. The helper will be coming to your house on {date} at {time} as you requested for communication with the helper you can vist his profile to check his/her details. Link Below👇.
localhost:5000/helper/{id}

Thank you for choosing our services. If you have any further questions, feel free to contact us.

Best regards,
Beta Service Team'''

    mail.send(msg)

# Routes        

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# search
@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        helpers = Helper.query.filter(Helper.skills.contains(query)).all()
        return render_template('search_results.html', helpers=helpers)
    return redirect('/')

# Get All Helpers Endpoint
@app.route('/helpers')
def get_all_helpers():
    helpers = Helper.query.all()
    return render_template('helpers.html', helpers=helpers)

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        name = request.form['username']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        checkuser = User.query.filter_by(name=name).first()
        checkemail = User.query.filter_by(email=email).first()
        if checkemail or checkuser:
            flash('Email or Username already exists. Please try again.')
            return redirect('/register')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            user = User(name=name, phone_number=phone_number, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.')
            return redirect('/login')
    return render_template('register.html')

# Helper Registration
@app.route('/register_helper', methods=['GET', 'POST'])
def register_helper():
    if 'helper_id' in session:
        return redirect('/helper_dashboard')
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        skills = request.form['skills']
        checkuser = Helper.query.filter_by(name=name).first()
        checkemail = Helper.query.filter_by(email=email).first()
        if checkemail or checkuser:
            flash('Email or Username already exists. Please try again.')
            return redirect('/register')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            helper = Helper(name=name, phone_number=phone_number, email=email, password=hashed_password, skills=skills)
            db.session.add(helper)
            db.session.commit()
            flash('Registration successful! You can now log in as a helper.')
            return redirect('/login_helper')
    return render_template('register_helper.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            flash('Invalid email or password. Please try again.')
            return redirect('/login')
    return render_template('login.html')

# Helper Login
@app.route('/login_helper', methods=['GET', 'POST'])
def login_helper():
    if 'helper_id' in session:
        return redirect('/helper_dashboard')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        helper = Helper.query.filter_by(name=username).first()
        if helper and check_password_hash(helper.password, password):
            session['helper_id'] = helper.id
            return redirect('/helper_dashboard')
        else:
            flash('Invalid email or password. Please try again.')
            return redirect('/login_helper')
    return render_template('login_helper.html')

# Logout
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        flash("You have logged out successfully")
    if 'helper_id' in session:
        session.pop('helper_id', None)
        flash("You have logged out successfully")
    return redirect('/')

#display helper's porfile
@app.route('/helper/<int:helper_id>')
def helper_profile(helper_id):
    helper = Helper.query.filter_by(id=helper_id)
    return render_template('helper_profile.html', helpers=helper)

# User Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    user = User.query.get(user_id)
    help_requests = HelpRequest.query.filter_by(user_id=user_id)
    return render_template('dashboard.html', user=user, help_requests=help_requests)

# Helper Dashboard
@app.route('/helper_dashboard')
def helper_dashboard():
    if 'helper_id' not in session:
        return redirect('/login_helper')
    else:
        helper_id = session['helper_id']
        helper = Helper.query.get(helper_id)
        help_requests = HelpRequest.query.filter_by(helper_id=helper_id)
        return render_template('helper_dashboard.html', helper=helper, help_requests=help_requests)

# Unapproved Requests
@app.route('/unapproved_requests')
def unapproved_requests():
    if 'helper_id' not in session:
        return redirect('/login_helper')
    helper_id = session['helper_id']
    helper = Helper.query.get(helper_id)
    unapproved_requests = HelpRequest.query.filter_by(status='Pending').all()
    return render_template('unapproved_requests.html', requests=unapproved_requests, helper=helper)

# Create Delivery Help Request
@app.route('/create_help_request', methods=['GET', 'POST'])
def create_help_request():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        task = request.form['task']
        address = request.form['address']
        time = request.form['time']
        date = request.form['date']
        desc = request.form['desc']
        user_id = session['user_id']
        help_request = HelpRequest(task=task, address=address, time=time, date=date, desc=desc, user_id=user_id)
        db.session.add(help_request)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('create_help_request.html')

# Helper Request Approval
@app.route('/approve_request/<int:request_id>', methods=['GET'])
def approve_request(request_id):
    if 'helper_id' not in session:
        return redirect('/login')
    else:
        helper_id = session['helper_id']
        helper = Helper.query.get(helper_id)
        request = HelpRequest.query.get(request_id)
        if request.helper_id is not None:
            flash('This request has already been assigned to another helper.')
            return redirect('/dashboard')
        request.status = 'approved'
        request.helper_id = helper.id
        db.session.commit()
        flash('Request approved successfully!')
        user = User.query.filter_by(id=request.user_id).first()
        user_email = user.email
        helpers = Helper.query.filter_by(id=request.helper_id).first()
        send_approval_email(user_email, request.time, request.date, request.task, helpers.name, user.id)
    return redirect('/dashboard')

# Update Help Request Status (Accept or Decline)
@app.route('/update_request_status/<int:help_request_id>/<status>')
def update_request_status(help_request_id, status):
    if 'helper_id' not in session:
        return redirect('/login_helper')
    helper_id = session['helper_id']
    help_request = HelpRequest.query.get(help_request_id)
    if help_request.helper_id != helper_id:
        flash('You are not authorized to update the status of this request.')
        return redirect('/helper_dashboard')
    help_request.status = status
    db.session.commit()
    flash('Request status updated successfully!')
    return redirect('/helper_dashboard')

# Contact Us
@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        msg = Message('Contact Us - Inquiry', sender=email, recipients=['betawebsiteproject@gmail.com'])  # Update with your email
        msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        mail.send(msg)
        flash('Your message has been sent. We will get back to you soon.')
        return redirect('/contact_us')
    return render_template('contact_us.html')

#error
app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
