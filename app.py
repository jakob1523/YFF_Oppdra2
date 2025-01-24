from flask import Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mariadb


app = Flask(__name__)
app.secret_key = "hemmeligpassord"  
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  

DB_CONFIG = {
    'host': 'localhost',
    'user': 'jakob-flask',
    'password': '123',
    'database': 'bok_oversetter'
}
#-u Geir Petter Torgersen -p 123 

def get_db_connection():
    return mariadb.connect(**DB_CONFIG)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return User(id=user[0], username=user[1])
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.username)
    return render_template('home.html')

    
@app.route('/adminside')
@login_required
def adminside():
    
    if current_user.username != "Geir Petter Torgersen":  
        return redirect(url_for('home'))  

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password, created_at FROM user")
    users = cursor.fetchall()
    cursor.execute("SELECT id, username, bok, bestill, created_at FROM bestilling")
    bestillinger = cursor.fetchall()

    cursor.close()
    conn.close()
     
    return render_template('adminside.html', users=users, bestillinger=bestillinger)

@app.route('/delete', methods=['POST'])
def slett():
    navn = request.form['navn']
    brukerid = request.form['brukerid']
    if navn != "Geir Petter Torgersen":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = %s", (brukerid,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('adminside'))
    else:
        return redirect(url_for('adminside'))

@app.route('/delete_bestill', methods=['POST'])
def slett_b():
    brukerid = request.form['brukerid']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bestilling WHERE id = %s", (brukerid,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('adminside'))

@app.route('/oversetter', methods=['GET', 'POST'])
@login_required
def oversetter():
    if request.method == 'POST':
        username = current_user.username  
        bok = request.form['bok']
        bestilling = request.form['bestilling']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bestilling (username, bok, bestill) VALUES (%s, %s, %s)", (username, bok, bestilling))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('kvittering'))

    return render_template('bestill.html')

@app.route('/kvittering', methods=['GET', 'POST'])
@login_required
def kvittering():
        return render_template('kvittering.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
       
        return redirect(url_for('login'))
       
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):   
            user_obj = User(id=user[0], username=user[1])
            login_user(user_obj)
            return redirect(url_for('home'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
